"""Chrome + PG LOCAL thật; Firebase/model fixture có nhãn, không phải LIVE."""
import os,sys,json,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import websockets,httpx,psycopg
import browser_smoke as h
from postgres_fixture import LocalPostgres
from test_advisor30_profile import ANSWERS,RAW
from career_library import catalog
CHECKS=[]

def install_fixture():
 import advisor.graph as graph,advisor.routes as routes
 from browser_fixture import app
 graph.demo_mode=lambda:False;routes.demo_mode=lambda:False
 evidence={'analysis':0,'chat':0,'delete':0,'create':0,'fail_next':False,'private_profile_sent':False}
 @app.middleware('http')
 async def counts(request,call_next):
  if request.method=='DELETE' and request.url.path=='/api/ai/data':evidence['delete']+=1
  if request.method=='POST' and request.url.path=='/api/ai/sessions':evidence['create']+=1
  return await call_next(request)
 @app.get('/__qa/removal')
 def state():return evidence
 @app.post('/__qa/removal/fail-once')
 def fail():evidence['fail_next']=True;return {'fixture':True}
 async def fake(payload,**kwargs):
  prompt=payload['messages'][0]['content']
  if 'Phân tích CÙNG LÚC' in prompt:
   evidence['analysis']+=1
   if evidence['fail_next']:evidence['fail_next']=False;raise httpx.ReadTimeout('synthetic fixture interruption')
   raw=copy.deepcopy(RAW)
   raw['career_directions']=[{'career_id':c.career_id,'reason':'Hướng khám phá dựa trên sở thích Tin học và vẽ, chưa đánh giá năng lực.','evidence':[{'question_id':1,'excerpt':'Tin học và vẽ'}],'subjects':['Tin học','Mỹ thuật'],'skills':['Giải quyết vấn đề'],'activities':['Thiết kế một ý tưởng trên giấy với bạn bè']} for c in catalog().careers[:3]]
   return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(raw,ensure_ascii=False)},'finish_reason':'stop'}]})
  if 'bộ nén ngữ cảnh' in prompt.lower():return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps({'profile':{'interests':[],'strengths':[],'growth_skills':[],'careers':[]},'summary':'Ghi chú kiểm thử riêng trong phiên.'})},'finish_reason':'stop'}]})
  evidence['chat']+=1;evidence['private_profile_sent']=any('HỒ SƠ ĐÃ XÁC NHẬN' in m['content'] for m in payload['messages'])
  return httpx.Response(200,json={'choices':[{'message':{'content':'**GIẢ LẬP KIỂM THỬ · chưa gọi DeepSeek.** Mình cùng tìm hiểu kỹ năng trong cuộc trò chuyện này nhé.'},'finish_reason':'stop'}]})
 graph.post_completion=fake

def passed(label):CHECKS.append(label);print('PASS '+label,flush=True)

async def checks(url,origin):
 async with websockets.connect(url,origin='http://localhost:9227',max_size=20000000) as ws:
  b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
  async def wait(expr):await b.wait_for('Boolean('+expr+')',timeout=40)
  async def click(expr):await b.evaluate(expr+'.click()')
  async def stats():return await b.evaluate("fetch('/__qa/removal').then(r=>r.json())")
  async def no_profile():assert await b.evaluate("!document.querySelector('#open-profile,#profile-dialog,#profile-content,#use-profile,.profile-proposal,.profile-item')")
  async def ready():await wait("document.querySelector('#chat-app')?.hidden===false&&!document.querySelector('#start-chat').disabled")
  async def answer_survey():
   await wait("document.querySelector('#career-survey')?.hidden===false&&!document.querySelector('#survey-next').disabled")
   for answer in ANSWERS:await b.evaluate("document.querySelector('#survey-answer').value="+json.dumps(answer)+";document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
  async def analyzed():await wait("document.querySelectorAll('.survey-direction').length===3&&document.querySelector('#thinking').hidden")
  await b.call('Page.navigate',{'url':origin+'/ai-career-advisor'});await answer_survey();await analyzed();await no_profile()
  sid=await b.evaluate("new URLSearchParams(location.search).get('conversation')")
  assert sid and (await stats())['analysis']==1 and (await stats())['chat']==0
  assert await b.evaluate("fetch('/api/ai/config').then(r=>r.json()).then(r=>r.guest_quota.remaining===8)")
  assert await b.evaluate("fetch('/api/ai/sessions/"+sid+"/retain',{method:'POST'}).then(r=>r.status===403)")
  passed('Guest: five answers auto-analyzed in chat once, three directions, quota8, no profile, retain403')
  await b.evaluate("document.querySelector('#message-input').value='Giải thích một kỹ năng cần rèn';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
  await wait("document.querySelector('#thinking').hidden&&document.querySelector('#messages').textContent.includes('GIẢ LẬP KIỂM THỬ')")
  assert await b.evaluate("fetch('/api/ai/config').then(r=>r.json()).then(r=>r.guest_quota.remaining===7)")
  before=await stats();await b.evaluate("document.querySelector('#message-input').value='Bản nháp cần giữ';document.querySelector('#message-input').dispatchEvent(new Event('input'))")
  await click("document.querySelector('.survey-direction .career-navigation-link')");await wait("document.querySelector('#content-dialog')?.open")
  await wait("[...document.querySelectorAll('#content-dialog a')].some(a=>a.textContent.includes('Xem truyện'))")
  await click("[...document.querySelectorAll('#content-dialog a')].find(a=>a.textContent.includes('Xem truyện'))")
  await wait("document.querySelector('#story-detail')?.hidden===false");await click("document.querySelector('#back-career')")
  await wait("document.querySelector('#content-dialog')?.open&&[...document.querySelectorAll('#content-dialog a')].find(a=>new URL(a.href).pathname==='/ai-career-advisor')");await click("[...document.querySelectorAll('#content-dialog a')].find(a=>new URL(a.href).pathname==='/ai-career-advisor')");await ready();await analyzed()
  assert await b.evaluate("new URLSearchParams(location.search).get('conversation')==="+json.dumps(sid)+"&&document.querySelector('#message-input').value==='Bản nháp cần giữ'")
  await b.evaluate('history.back()');await wait("document.querySelector('#content-dialog')?.open");await b.evaluate('history.forward()');await ready();await analyzed()
  await b.call('Page.reload');await ready();await analyzed();after=await stats()
  assert before==after and await b.evaluate("document.querySelectorAll('.survey-analysis-result').length===1")
  assert len([x for x in (await b.call('Target.getTargets'))['targetInfos'] if x['type']=='page'])==1
  passed('Guest: library/story/back-forward/reload preserve same chat, survey, draft, one tab; zero model/create calls')
  await click("document.querySelector('#guest-login')");await wait("document.querySelector('#auth-dialog')?.open&&!document.querySelector('#google-signin').disabled")
  await click("document.querySelector('#google-signin')")
  await wait("document.querySelector('#guest-banner')?.hidden===true&&document.querySelector('#keep-conversation')?.hidden===false");await analyzed();await no_profile()
  assert await b.evaluate("new URLSearchParams(location.search).get('conversation')==="+json.dumps(sid))
  await click("document.querySelector('#keep-conversation')");await wait("document.querySelector('#action-dialog').open");await click("document.querySelector('#confirm-action')")
  await wait("document.querySelector('#session-note').textContent.includes('Lịch sử đã bật')")
  await b.call('Page.reload');await ready();await analyzed()
  assert await b.evaluate("new URLSearchParams(location.search).get('conversation')==="+json.dumps(sid))
  passed('Member fixture login claims Guest history, retains identical ID/survey/messages, reload persistent chat')
  await b.evaluate("fetch('/__qa/removal/fail-once',{method:'POST'})");await click("document.querySelector('#new-chat')");await click("document.querySelector('#start-chat')");await answer_survey()
  await wait("document.querySelector('.analysis-retry')&&!document.querySelector('#thinking').hidden===false")
  failed=await stats();await click("document.querySelector('.analysis-retry')");await analyzed()
  assert (await stats())['analysis']==failed['analysis']+1 and await b.evaluate("document.querySelectorAll('.survey-analysis-result').length===1")
  await b.call('Page.reload');await ready();await analyzed();assert (await stats())['analysis']==failed['analysis']+1
  passed('Member: failed analysis visible in chat; explicit retry once, no duplicate result or automatic repeat on reload')
  for width in (1440,390):
   await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':900 if width==1440 else 844,'deviceScaleFactor':1,'mobile':width<500})
   await no_profile();assert await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1');await b.screenshot('profile-removal-'+str(width)+'.png')
  passed('Premium desktop/mobile: no profile UI, no overflow, visible inline analysis')
  await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':900,'deviceScaleFactor':1,'mobile':False})
  await click("document.querySelector('#delete-all-data')");await wait("document.querySelector('#action-dialog').open")
  await click("document.querySelector('#action-dialog [data-close-dialog]')");assert (await stats())['delete']==0
  await click("document.querySelector('#delete-all-data')");await wait("document.querySelector('#action-dialog').open");await click("document.querySelector('#confirm-action')")
  await wait("document.querySelector('#welcome').hidden===false&&document.querySelectorAll('.history-item').length===0")
  assert (await stats())['delete']==1 and not (await stats())['private_profile_sent'];assert not b.errors,b.errors
  passed('Account sidebar deletion: cancel does nothing, confirm deletes only own LOCAL fixture data; zero JS exceptions')
  (h.ARTIFACTS/'profile-removal-browser.json').write_text(json.dumps({'groups':CHECKS,'database':'isolated local PostgreSQL','firebase':'fixture NOT LIVE','deepseek':'fixture NOT LIVE','production':'untouched'},ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':
 for k in list(os.environ):
  if k.startswith(('DEEPSEEK_','FIREBASE_','SEARCH_','DATABASE_URL','ADVISOR_CONTROLLED')):os.environ.pop(k)
 with LocalPostgres() as cluster:
  with psycopg.connect(cluster.url,autocommit=True) as db:
   for f in ('001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql'):db.execute((h.ROOT/'migrations'/f).read_text(encoding='utf8'))
   db.execute("SET laban.profile_migration_target='task4-staging-approved'");db.execute((h.ROOT/'migrations/006_confirmed_career_profile.sql').read_text(encoding='utf8'))
  os.environ.update(LABAN_BROWSER_TEST_DATABASE=cluster.url,LABAN_BROWSER_NO_PROFILE='1',ADVISOR_PROFILE_ENABLED='true',DEEPSEEK_API_KEY='fixture-only-not-a-real-key')
  os.environ['PYTHONPATH']=str(h.ROOT)+os.pathsep+str(h.ROOT/'tests');h.checks=checks;h.main()
