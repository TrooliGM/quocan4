"""Chrome + PG LOCAL; Firebase/LLM fixture explicit, never label LIVE quality."""
import json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import websockets,psycopg
import browser_smoke as h
from postgres_fixture import LocalPostgres
from test_advisor30_profile import ANSWERS
CHECKS=[]
def passed(name):CHECKS.append(name);print('PASS '+name,flush=True)
async def checks(url,origin):
 async with websockets.connect(url,origin='http://localhost:9227',max_size=20000000) as ws:
  b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
  await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
  await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_discovery'})
  await b.wait_for("document.querySelector('#career-survey')?.hidden===false && !document.querySelector('#survey-next').disabled",timeout=40)
  for answer in ANSWERS:
   await b.evaluate("document.querySelector('#survey-answer').value="+json.dumps(answer)+";document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
  await b.wait_for("document.querySelector('#profile-dialog').open && document.querySelectorAll('.profile-proposal').length===2",timeout=40)
  facts=await b.evaluate("fetch('/__qa/advisor30').then(r=>r.json())")
  assert facts['analysis_calls']==1 and facts['main_calls']==0
  assert await b.evaluate("document.querySelectorAll('.profile-item').length===0 && !document.body.innerText.includes('Phân tích khảo sát qua AI Chat') && document.querySelector('#thinking').hidden")
  assert await b.evaluate("fetch('/api/ai/config').then(r=>r.json()).then(r=>r.guest_quota.remaining===8)")
  await b.screenshot('task41-auto-profile-desktop.png');passed('Five answers automatically produce proposals; zero chat questions charged; zero implicit confirmations')
  await b.evaluate("document.querySelector('.profile-proposal details').open=true;document.querySelectorAll('.profile-proposal')[1].querySelectorAll('button')[1].click()")
  await b.wait_for("document.querySelectorAll('.profile-proposal').length===1")
  await b.evaluate("(()=>{let t=document.querySelector('.profile-proposal textarea');t.value='Thiết kế đồ họa trên máy tính';t.dispatchEvent(new Event('input'));document.querySelector('.profile-proposal button').click()})()")
  await b.wait_for("document.querySelectorAll('.profile-item').length===1 && document.querySelectorAll('.profile-proposal').length===0")
  for _ in range(2):
   await b.evaluate("document.querySelector('#profile-dialog').close();document.querySelector('#open-profile').click()")
   await b.wait_for("document.querySelectorAll('.profile-item').length===1")
  facts=await b.evaluate("fetch('/__qa/advisor30').then(r=>r.json())");assert facts['analysis_calls']==1 and facts['main_calls']==0
  passed('Edit/accept/reject each item; opening profile reuses completed analysis without provider calls')
  # Browser transport failure, not a provider LIVE test. Draft must survive reopening.
  await b.evaluate("window.qaFetch=fetch;fetch=(u,o)=>String(u).includes('/career-profile/items/')&&o?.method==='PATCH'?Promise.resolve(new Response(JSON.stringify({detail:'fixture failure'}),{status:503})):qaFetch(u,o);(()=>{let t=document.querySelector('.profile-item input');t.value='Bản nháp chưa lưu';t.dispatchEvent(new Event('input'));document.querySelector('.profile-item button').click()})()")
  await b.wait_for("document.querySelector('.profile-status').textContent.includes('Những lựa chọn')")
  await b.evaluate("fetch=qaFetch;document.querySelector('#profile-dialog').close();document.querySelector('#open-profile').click()")
  await b.wait_for("document.querySelector('.profile-item input')?.value==='Bản nháp chưa lưu'")
  await b.evaluate("document.querySelector('.profile-item button').click()")
  await b.wait_for("document.querySelector('.profile-status').textContent==='Đã cập nhật.'")
  passed('Failed profile save preserves draft on reopen; retry saves without overwriting another owner')
  await b.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
  assert await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
  await b.screenshot('task41-auto-profile-mobile.png')
  await b.evaluate("document.querySelector('#profile-dialog').close();document.querySelector('#message-input').value='Giải thích ngắn một kỹ năng cần rèn';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
  await b.wait_for("document.querySelectorAll('.message-row').length===3 && document.querySelector('#thinking').hidden")
  assert await b.evaluate("document.querySelector('.assistant .message-bubble') && document.querySelector('.message-actions button') && !document.querySelector('.message-row.assistant img,.message-row.assistant .message-label')")
  assert await b.evaluate("fetch('/api/ai/config').then(r=>r.json()).then(r=>r.guest_quota.remaining===7)")
  facts=await b.evaluate("fetch('/__qa/advisor30').then(r=>r.json())");assert facts['analysis_calls']==1 and facts['main_calls']==1
  await b.screenshot('task41-chat-mobile.png');passed('Premium bubble/Copy/header retained; explicit Send charges exactly one chat; chat does not repeat analysis')
  # A new survey with one failed HTTP request: retry only after a visible failure.
  await b.evaluate("document.querySelector('#new-chat').click();document.querySelector('#start-chat').click()")
  await b.wait_for("document.querySelector('#career-survey').hidden===false && !document.querySelector('#survey-next').disabled")
  await b.evaluate("window.qaFetch=fetch;window.qaFailed=false;fetch=(u,o)=>String(u).endsWith('/analysis')&&o?.method==='POST'&&!qaFailed?(qaFailed=true,Promise.resolve(new Response(JSON.stringify({detail:'fixture interruption'}),{status:503}))):qaFetch(u,o)")
  for answer in ANSWERS:
   await b.evaluate("document.querySelector('#survey-answer').value="+json.dumps(answer)+";document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
  await b.wait_for("document.querySelector('#profile-dialog').open && [...document.querySelectorAll('#profile-content button')].some(b=>b.textContent==='Thử phân tích lại')",timeout=40)
  await b.evaluate("fetch=qaFetch;[...document.querySelectorAll('#profile-content button')].find(b=>b.textContent==='Thử phân tích lại').click()")
  await b.wait_for("document.querySelectorAll('.profile-proposal').length===2",timeout=40)
  facts=await b.evaluate("fetch('/__qa/advisor30').then(r=>r.json())");assert facts['analysis_calls']==2
  passed('Interrupted automatic request gives clear retry; no endless resubmission or extra chat charge')
  assert not b.errors,b.errors
  (h.ARTIFACTS/'task41-browser.json').write_text(json.dumps({'groups':CHECKS,'firebase':'fixture NOT LIVE','deepseek':'fixture NOT LIVE','database':'local isolated PostgreSQL'},ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':
 for k in list(os.environ):
  if k.startswith(('DEEPSEEK_','FIREBASE_','SEARCH_','DATABASE_URL','ADVISOR_CONTROLLED')):os.environ.pop(k)
 with LocalPostgres() as cluster:
  with psycopg.connect(cluster.url,autocommit=True) as db:
   for f in ['001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql']:db.execute((h.ROOT/'migrations'/f).read_text(encoding='utf8'))
   db.execute("SET laban.profile_migration_target='task4-staging-approved'");db.execute((h.ROOT/'migrations/006_confirmed_career_profile.sql').read_text(encoding='utf8'))
  os.environ.update(LABAN_BROWSER_TEST_DATABASE=cluster.url,LABAN_BROWSER_ADVISOR30='1',ADVISOR_PROFILE_ENABLED='true',DEEPSEEK_API_KEY='fixture-only-not-a-real-key')
  os.environ['PYTHONPATH']=str(h.ROOT)+os.pathsep+str(h.ROOT/'tests')
  h.checks=checks;h.main()
