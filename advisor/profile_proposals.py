"""Grounded conversation proposals, never consent or a confirmed-profile write."""
import json
import re
import logging
from typing import Literal
from uuid import uuid5,NAMESPACE_URL
from pydantic import BaseModel,ConfigDict,Field
from .survey_analysis import CATEGORIES
logger=logging.getLogger(__name__)

AREA_CATEGORY={'interests':'interests','self_reported_skills':'strengths','subjects':'interests','work_preferences':'work_preferences','goals':'growth_skills','experiences':'growth_skills','careers':'careers','uncertainties':'uncertainties'}
class Update(BaseModel):
    model_config=ConfigDict(extra='forbid')
    area:Literal['interests','self_reported_skills','subjects','work_preferences','goals','experiences','careers','uncertainties']
    value:str=Field(min_length=3,max_length=160)
    excerpt:str=Field(min_length=3,max_length=200)
    inference_type:Literal['trực tiếp','diễn giải','suy luận']
    operation:Literal['add','correct','withdraw']
    replaces:list[str]=Field(max_length=6)

def norm(value):return ' '.join(value.casefold().split())

def polarity_replacements(value,excerpt,category,existing):
    positive=re.sub(r'^(?:không(?: còn)?|chưa)\s+','',norm(value))
    if positive==norm(value) or len(positive.split())<3 or not re.search(r'\b(?:không|khong|chưa|chua)\b',excerpt,re.I):return []
    return [id for id,p in existing.items() if p['category']==category and norm(p['value'])==positive][:6]

def validate_updates(raw,state):
    if not isinstance(raw,list) or len(raw)>8:return []
    from .analysis_jobs import analysis_for_session
    analysis=analysis_for_session(state['session']) or {}
    existing={p['id']:p for p in analysis.get('proposed_profile_items',[])}
    result=[];seen=set()
    for item in raw:
        try:
            u=Update.model_validate(item)
            if u.excerpt not in state['message']:continue # Actual CURRENT user only, not assistant/web.
            if re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?:\d[ .+-]?){9,}',u.value+' '+u.excerpt):continue
            category=AREA_CATEGORY[u.area]
            if u.area in ('self_reported_skills','careers') and u.inference_type!='trực tiếp':continue
            if u.area=='self_reported_skills' and not re.search(r'biết|có thể|tự nhận|làm được|thường|đã|từng|giỏi|thành thạo|kiên nhẫn',u.excerpt,re.I):continue
            # A narrow consistency fence: exact same statement with opposite
            # polarity and an actual denial in the user quote. Never job rules.
            if u.operation=='add':
                matches=polarity_replacements(u.value,u.excerpt,category,existing)
                if matches:u.operation='correct';u.replaces=matches
            if u.operation!='add' and (not u.replaces or any(x not in existing for x in u.replaces)):continue
            if u.operation=='add' and u.replaces:continue
            if any(existing[x]['category']!=category for x in u.replaces):continue
            key=(category,norm(u.value))
            if key in seen:continue
            seen.add(key)
            proposal_id=str(uuid5(NAMESPACE_URL,state['session_id']+u.area+norm(u.value)))
            result.append({'id':proposal_id,'category':category,'area':u.area,'value':u.value,
                'evidence':[{'request_id':state['request_id'],'excerpt':u.excerpt}],
                'evidence_question_ids':[], 'confidence':'rõ ràng' if u.inference_type=='trực tiếp' else 'cần xác nhận',
                'inference_type':u.inference_type,'proposed_action':'confirm' if u.inference_type!='suy luận' and u.operation!='withdraw' else 'clarify',
                'operation':u.operation,'replaces':u.replaces,
                'previous_values':[existing[x]['value'] for x in u.replaces]})
        except (ValueError,TypeError,KeyError):continue
    return result

def decode_updates(message,state):
    calls=message.get('tool_calls') or []
    if len(calls)!=1:return []
    from .navigation import TOOL_NAME
    fn=calls[0].get('function',{})
    if fn.get('name')!=TOOL_NAME:return []
    try:
        arguments=fn.get('arguments','')
        if not isinstance(arguments,str) or len(arguments)>24000:return []
        raw=json.loads(arguments)
        if not isinstance(raw,dict):return []
        supplied=raw.get('profile_updates');accepted=validate_updates(supplied,state)
        if isinstance(supplied,list) and len(accepted)<len(supplied):logger.warning('profile_proposals_rejected supplied=%d accepted=%d',len(supplied),len(accepted))
        return accepted
    except (ValueError,TypeError):return []

def merge(session,base):
    rows={p['id']:dict(p) for p in (base or {}).get('proposed_profile_items',[])}
    changes=[]
    for message in session.get('messages',[]):
        if message.get('role')!='assistant':continue
        for p in message.get('profile_updates',[])[:8]:
            if not isinstance(p,dict) or p.get('category') not in CATEGORIES or not p.get('id'):continue
            # Survey analysis may commit after the chat update. Reconcile the
            # same grounded polarity fence at read time without changing history.
            if p.get('operation')=='add':
                matches=polarity_replacements(p['value'],' '.join(e.get('excerpt','') for e in p.get('evidence',[])),p['category'],rows)
                if matches:p={**p,'operation':'correct','replaces':matches,'previous_values':[rows[id]['value'] for id in matches]}
            for old in p.get('replaces',[]):rows.pop(old,None)
            if p.get('operation')!='withdraw':
                duplicate=next((key for key,value in rows.items() if value['category']==p['category'] and norm(value['value'])==norm(p['value'])),None)
                if duplicate is None:rows[p['id']]=p
            if p.get('operation') in ('correct','withdraw'):changes.append(p)
    if not base and not rows and not changes:return None
    survey=(session.get('messages') or [{}])[0].get('survey',{})
    return {**(base or {}),'survey_id':(base or {}).get('survey_id',survey.get('analysis_request_id')),
        'conversation_id':session.get('id'),'summary':(base or {}).get('summary','Các thông tin bạn vừa tự chia sẻ đang được đề xuất để xem lại; chưa là hồ sơ đã xác nhận.'),
        'proposed_profile_items':list(rows.values())[-80:],'clarification_questions':(base or {}).get('clarification_questions',[]),
        'changes':changes[-12:],'analysis_version':2}
