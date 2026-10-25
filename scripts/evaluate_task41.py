"""Evaluate authorized QA backend URLs. Raw synthetic samples in artifacts only.

This records execution, not automatic quality PASS; human rubric review is required.
No API key is needed here: requests use an authorized Firebase QA ID token.
"""
import json,re,time
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
CASES=json.loads((ROOT/'tests/fixtures/task41-eval.json').read_text(encoding='utf8'))['cases']
NEUTRAL=['Chưa rõ sở thích','Muốn thử hoạt động mới','Chưa rõ điểm mạnh','Muốn hiểu nhiều môi trường','Muốn được giải thích dễ hiểu']
ANALYSIS='Hãy phân tích khảo sát của em, gợi ý khoảng 3 nhóm nghề cùng lý do, môn học, kỹ năng và trải nghiệm để thử.'
def evaluate_case(api,case,phase):
 session=api.call('POST','/api/ai/sessions',{'remember':False,'mode':case.get('mode','career_discovery'),**({'career_id':case['career_id']} if case.get('career_id') else {})},201).json()['session']
 sid=session['id'];row=api.call('PUT','/api/ai/sessions/'+sid+'/survey',{'answers':case.get('answers',NEUTRAL),'address':'anh'}).json()['session']
 if case.get('profile_on'):api.call('PUT','/api/ai/sessions/'+sid+'/profile-use',{'use_profile':True})
 turns=[]
 for message in ([ANALYSIS] if case.get('type')=='analysis' else case['messages']):
  start=time.monotonic()
  if case.get('type')=='analysis' and phase=='after':
   response=api.call('POST','/api/ai/sessions/'+sid+'/analysis',{})
   data=response.json();answer=(data.get('result') or {}).get('summary','');analysis=data.get('result');status=data.get('status')
  else:
   response=api.call('POST','/api/ai/chat',{'session_id':sid,'request_id':str(uuid4()),'message':message})
   data=response.json()['session']['messages'][-1];answer=data['content'];analysis=data.get('survey_analysis');status=data.get('analysis_status')
  timing=response.headers.get('server-timing','')
  metrics={k:int(v) for k,v in re.findall(r'(llm_calls|llm_input_tokens|llm_output_tokens);desc="(\d+)"',timing)}
  turns.append({'answer':answer,'analysis':analysis,'analysis_status':status,'seconds':round(time.monotonic()-start,3),'search_status':data.get('search_status'),'sources':data.get('sources',[]),'profile_read':'profile_context_load' in timing,'metrics':metrics})
 return {'id':case['id'],'title':case['title'],'phase':phase,'execution':'PASS','quality':'UNREVIEWED','requires_search':case.get('requires_search',False),'expect':case['expect'],'mode':row['messages'][0].get('career_context'),'turns':turns}
if __name__=='__main__':
 raise SystemExit('Import evaluate_case with an authorized QA API client; see docs/task41-checkpoint.md. Do not put tokens in command arguments or source.')
