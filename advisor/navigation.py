"""Model-proposed intent, server-owned destinations. No URL/tool execution from AI."""
import json
import re
from functools import lru_cache
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from career_library import catalog, find_career, normalize_search

Kind=Literal['career_profile','career_story','career_exploration']
TOOL_NAME='present_laban_actions'


@lru_cache(maxsize=1)
def _names():
    mapping={normalize_search(c.name):c.career_id for c in catalog().careers}
    pattern=re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(name) for name in sorted(mapping,key=len,reverse=True))+r')(?!\w)')
    return mapping,pattern


def mentioned_ids(text):
    mapping,pattern=_names()
    return list(dict.fromkeys(mapping[m[0]] for m in pattern.finditer(normalize_search(text))))


def reference_context(state):
    """A narrow ambiguity fence, not an intent router. Model still resolves intent.

    Do not let a model/source silently choose one of several just-mentioned jobs.
    Names and IDs come from the catalog; no profession-specific keyword rules.
    """
    text=normalize_search(state['message'])
    if not re.search(r'\b(?:nghe|nganh|cai) (?:do|ay|nay)\b',text) or mentioned_ids(text):return {'status':'not_ambiguous'}
    history=state.get('session',{}).get('messages',[])[-12:]
    latest_user=next((m.get('content','') for m in reversed(history) if m.get('role')=='user'),'')
    if len(mentioned_ids(latest_user))==1:return {'status':'not_ambiguous'}
    last=next((m for m in reversed(history) if m.get('role')=='assistant'),{})
    ids=mentioned_ids(last.get('content',''))
    for action in last.get('navigation_actions',[]) or []:
        try:
            valid=NavigationAction.model_validate(action)
            if valid.career_id and valid.career_id not in ids:ids.append(valid.career_id)
        except (ValueError,TypeError):continue
    return {'status':'ambiguous','candidates':[{'career_id':id,'name':find_career(id).name} for id in ids]} if len(ids)>1 else {'status':'not_ambiguous'}


def destination(kind, career_id):
    career=find_career(career_id) if career_id is not None else None
    if career_id is not None and not career:raise ValueError('unknown_career')
    if kind=='career_profile':
        return ('Xem hồ sơ · '+career.name,'/?career='+career_id+'#careers') if career else ('Khám phá 200 nghề','/#careers')
    if kind=='career_story':
        if career:
            from story_library import get_story
            if not get_story(career_id):raise ValueError('story_unavailable')
        return ('Xem truyện · '+career.name,'/mot-ngay-lam-viec?nghe='+career_id) if career else ('Thư viện Truyện nghề','/mot-ngay-lam-viec')
    if kind=='career_exploration' and career:
        return ('Cùng tìm hiểu · '+career.name,'/ai-career-advisor?mode=career_exploration&career_id='+career_id)
    raise ValueError('unknown_destination')


class NavigationAction(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind:Kind
    career_id:str | None=None
    label:str=Field(max_length=180)
    href:str=Field(max_length=240)

    @model_validator(mode='after')
    def canonical(self):
        if (self.label,self.href)!=destination(self.kind,self.career_id):raise ValueError('noncanonical_navigation')
        return self


class Proposal(BaseModel):
    model_config=ConfigDict(extra='forbid')
    kind:Kind
    career_id:str | None=None


def actions_from_proposal(raw, state):
    """Source text is not user intent. Require a real user quote as intent basis."""
    if raw.get('intent') not in ('navigate','explore_options'):return []
    basis=raw.get('basis')
    if not isinstance(basis,str) or not 2<=len(basis)<=240:return []
    users=[state['message']]+[m.get('content','') for m in state.get('session',{}).get('messages',[])[-12:] if m.get('role')=='user']
    if not any(normalize_search(basis) in normalize_search(text) for text in users):return []
    proposals=raw.get('actions');result=[];seen=set()
    if not isinstance(proposals,list) or len(proposals)>4:return []
    for item in proposals:
        try:
            p=Proposal.model_validate(item);label,href=destination(p.kind,p.career_id)
            if href in seen:continue
            seen.add(href)
            result.append(NavigationAction(kind=p.kind,career_id=p.career_id,label=label,href=href).model_dump())
        except (ValueError,TypeError):continue
    return result


def decode_completion(message,state):
    """Same completion, optional terminal function; never dispatch arbitrary tools."""
    content=message.get('content');actions=[]
    calls=message.get('tool_calls') or []
    if len(calls)==1:
        fn=calls[0].get('function',{})
        if fn.get('name')==TOOL_NAME:
            arguments=fn.get('arguments','')
            if isinstance(arguments,str) and len(arguments)<=24000:
                try:
                    raw=json.loads(arguments)
                    if isinstance(raw,dict) and isinstance(raw.get('answer'),str) and raw['answer'].strip():
                        content=raw['answer'];actions=actions_from_proposal(raw,state)
                except (ValueError,TypeError):pass
    reference=reference_context(state)
    if reference['status']=='ambiguous':
        # Preserve a model-written clarification if it refrained from choosing.
        if calls or not isinstance(content,str) or '?' not in content:
            names=[r['name'] for r in reference['candidates'][:4]]
            content='Bạn đang nhắc đến '+', '.join(names)+' hay một nghề khác?'
        actions=[]
    return content,actions


def tool():
    return {'type':'function','function':{'name':TOOL_NAME,
        'description':'Trả lời cuối bằng tiếng Việt và đề xuất nút nội bộ La Bàn khi lời học sinh yêu cầu hoặc nhu cầu khám phá có căn cứ. Không thực thi công cụ bên ngoài.',
        'parameters':{'type':'object','properties':{
            'answer':{'type':'string','description':'Câu trả lời Markdown tự nhiên cho học sinh, không URL. Không tự kết luận phù hợp tuyệt đối.'},
            'intent':{'type':'string','enum':['navigate','explore_options']},
            'basis':{'type':'string','description':'Trích nguyên một cụm từ lời học sinh trong câu hiện tại/lịch sử gần, không từ web hay lời AI.', 'maxLength':240},
            'actions':{'type':'array','maxItems':4,'items':{'type':'object','properties':{
                'kind':{'type':'string','enum':['career_profile','career_story','career_exploration']},
                'career_id':{'type':['string','null'],'description':'ID đúng từ danh mục; null chỉ để mở thư viện nghề/truyện khi chưa chỉ định nghề.'}},
                'required':['kind','career_id'],'additionalProperties':False}}},
            'required':['answer','intent','basis','actions'],'additionalProperties':False}}}


@lru_cache(maxsize=1)
def directory():
    return '\n'.join(c.career_id+' | '+c.name for c in catalog().careers)


def context(state):
    refs=[]
    for m in state.get('session',{}).get('messages',[])[-12:]:
        if m.get('role')!='assistant':continue
        valid=[]
        for item in (m.get('navigation_actions') or [])[:4]:
            try:valid.append(NavigationAction.model_validate(item).model_dump())
            except (ValueError,TypeError):continue
        if valid:refs.append(valid)
    career_context=(state.get('session',{}).get('messages') or [{}])[0].get('career_context',{})
    return {'recent_action_groups':refs[-4:],'current_career':career_context.get('career_id'),'reference':reference_context(state)}
