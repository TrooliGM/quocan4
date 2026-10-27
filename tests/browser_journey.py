"""Actual FastAPI pages + isolated local PG. Firebase fixture, no provider calls."""
import asyncio,json,os,sys
from pathlib import Path
import websockets,psycopg
import browser_smoke as h
from postgres_fixture import LocalPostgres
ROOT=Path(__file__).resolve().parents[1]
INIT=r'''const f=fetch;window.fetch=(u,o={})=>{const path=String(u);if(path.startsWith('/api/')){const rows=JSON.parse(sessionStorage.getItem('__journey_requests')||'[]');rows.push({path:path.split('?')[0],method:o.method||'GET'});sessionStorage.setItem('__journey_requests',JSON.stringify(rows));}return f(u,o);};'''
async def checks(wsurl,origin):
 async with websockets.connect(wsurl,origin='http://localhost:9227',max_size=20000000) as ws:
  b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable');await b.call('Page.addScriptToEvaluateOnNewDocument',{'source':INIT})
  async def wait(s):await b.wait_for("Boolean("+s+")",timeout=40)
  async def tabs():return len([x for x in (await b.call('Target.getTargets'))['targetInfos'] if x['type']=='page'])
  async def click(s):await b.call('Runtime.evaluate',{'expression':s+'.click()','userGesture':True})
  async def ready():await wait("document.querySelector('#chat-app')?.hidden===false&&!document.querySelector('#start-chat').disabled")
  async def buttons(ids):
   await b.evaluate("(async()=>{const {navigationButtons}=await import('/assets/navigation-actions.js?v=task44-1');document.querySelector('#messages').append(navigationButtons("+json.dumps(ids)+"))})()")
  await b.call('Page.navigate',{'url':origin+'/ai-career-advisor'})
  await ready();await wait("document.querySelector('#career-survey')?.hidden===false")
  sid=await b.evaluate("new URLSearchParams(location.search).get('conversation')");assert sid
  catalog=await b.evaluate("fetch('/api/career-library?limit=3').then(r=>r.json()).then(d=>d.items)");id1,id2,id3=[c['career_id'] for c in catalog]
  base=await tabs();assert base==1
  # Incomplete survey, safe draft and original session survive same-tab profile trip.
  await b.evaluate("document.querySelector('#survey-answer').value='Em thích vẽ';document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
  await wait("document.querySelector('#survey-step').textContent.includes('2 / 5')")
  await b.evaluate("document.querySelector('#survey-answer').value='Chưa gửi bước hai';document.querySelector('#survey-answer').dispatchEvent(new Event('input'))")
  # Survey hides message list, use real header logo (same shared navigation).
  await click("document.querySelector('a[href^=\"/\"]')")
  await wait("document.querySelector('#library-categories')?.children.length===12")
  await b.evaluate("window.openLibraryCareer("+json.dumps(id1)+")")
  await wait("document.querySelector('#content-dialog').open&&document.querySelector('.library-modal-actions')")
  await click("document.querySelector('.library-modal-actions a')")
  await ready();await wait("document.querySelector('#survey-step')?.textContent.includes('2 / 5')")
  assert await b.evaluate("new URLSearchParams(location.search).get('conversation')==="+json.dumps(sid)+"&&document.querySelector('#survey-answer').value==='Chưa gửi bước hai'")
  # Complete survey using real API fixture, not LLM; reopening must not call analysis.
  await b.evaluate("(async()=>{await fetch('/api/ai/sessions/"+sid+"/survey',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers:['Thích vẽ','Tìm hiểu máy tính','Kiên nhẫn','Làm việc nhóm','Muốn hiểu nghề'],address:'chị'})})})()")
  await b.call('Page.reload');await ready();await wait("!document.querySelector('#message-form').hidden")
  await b.evaluate("document.querySelector('#message-input').value='Bản nháp chưa gửi';document.querySelector('#message-input').dispatchEvent(new Event('input'));sessionStorage.setItem('__journey_requests','[]')")
  actions=[{'kind':'career_profile','career_id':id1,'label':'Profile fixture','href':'/?career='+id1+'#careers'},{'kind':'career_story','career_id':id1,'label':'Story fixture','href':'/mot-ngay-lam-viec?nghe='+id1}]
  await buttons(actions);await click("document.querySelector('.career-navigation-link')")
  await wait("document.querySelector('#content-dialog')?.open&&document.querySelector('.library-modal-actions')")
  for career in [id2,id3]:
   await b.evaluate('window.openLibraryCareer('+json.dumps(career)+')');await wait("document.querySelector('.library-modal-actions a')?.href.includes("+json.dumps('career_id='+career)+")")
  await b.evaluate('history.back()');await wait("document.querySelector('.library-modal-actions a')?.href.includes("+json.dumps('career_id='+id2)+")")
  await b.evaluate('history.forward()');await wait("document.querySelector('.library-modal-actions a')?.href.includes("+json.dumps('career_id='+id3)+")")
  await click("document.querySelector('.library-modal-actions a')");await ready();await wait("document.querySelector('#message-input')?.value==='Bản nháp chưa gửi'")
  await buttons(actions);await click("[...document.querySelectorAll('.career-navigation-link')].find(a=>a.href.includes('mot-ngay'))")
  await wait("document.querySelector('#story-detail')?.hidden===false")
  await click("document.querySelector('#tab-comic')");await click("document.querySelector('#next-scene')")
  await click("document.querySelector('.topbar a[href*=ai-career-advisor]')" if await b.evaluate("!!document.querySelector('.topbar a[href*=ai-career-advisor]')") else "document.querySelector('a[href*=ai-career-advisor]')")
  await ready();await wait("document.querySelector('#message-input')?.value==='Bản nháp chưa gửi'")
  await b.evaluate('history.back()');await wait("document.querySelector('#story-detail')?.hidden===false")
  await b.evaluate('history.forward()');await ready();await wait("document.querySelector('#message-input')?.value==='Bản nháp chưa gửi'")
  # Scene handoff returns to original session, no second survey and no auto-send.
  await buttons(actions);await click("[...document.querySelectorAll('.career-navigation-link')].find(a=>a.href.includes('mot-ngay'))")
  await wait("document.querySelector('#story-detail')?.hidden===false")
  await click("document.querySelector('#tab-comic')");await click("document.querySelector('#ask-scene')")
  await b.evaluate("document.querySelector('#story-question').value='Cảnh này cần kỹ năng gì?';document.querySelector('#story-ask-form').requestSubmit()")
  await ready();await wait("document.querySelector('#message-input')?.value==='Bản nháp chưa gửi'")
  assert await b.evaluate("new URLSearchParams(location.search).get('conversation')==="+json.dumps(sid)+"&&document.querySelector('#career-survey').hidden")
  req=await b.evaluate("JSON.parse(sessionStorage.getItem('__journey_requests'))")
  assert not [r for r in req if r['method']!='GET' and r['path']!='/api/ai/guest/session' and not(r['method']=='PUT' and r['path'].endswith('/exploration'))],req
  assert await tabs()==base
  # Firebase popup/claim fixture only; not a real Google human authentication.
  await click("document.querySelector('#guest-login')");await wait("document.querySelector('#auth-dialog')?.open&&!document.querySelector('#google-signin').disabled")
  await click("document.querySelector('#google-signin')");await ready();await wait("document.querySelector('#guest-banner')?.hidden===true")
  assert await b.evaluate("new URLSearchParams(location.search).get('conversation')==="+json.dumps(sid)+"&&document.querySelector('#message-input').value==='Bản nháp chưa gửi'&&document.querySelector('#career-survey').hidden")
  assert await tabs()==base
  for width in [1440,390]:
   await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':844,'deviceScaleFactor':1,'mobile':width<500})
   assert await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   await b.screenshot('task44-local-'+str(width)+'.png')
  report={'actual_pages':'PASS local FastAPI+PG','same_tab_profile_story_scene':'PASS','multi_career_back_forward':'PASS','survey_draft_original_id':'PASS','zero_chat_create_analysis_calls':True,'journey_metadata_put':'allowed, no quota charge','guest_cookie_verification_posts':'allowed, existing identity only','tabs_before':base,'tabs_after':await tabs(),'firebase_google_claim':'PASS fixture only, real popup NOT TESTED','desktop_mobile':'PASS'}
  (ROOT/'artifacts/task44-journey-local.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
if __name__=='__main__':
 for k in list(os.environ):
  if k.startswith(('DEEPSEEK_','FIREBASE_','SEARCH_','DATABASE_URL')):os.environ.pop(k)
 os.environ['LABAN_TEST_PG_BIN']='D:/khkt/artifacts/postgres-tools/pgsql/bin'
 with LocalPostgres() as pg:
  with psycopg.connect(pg.url,autocommit=True) as db:
   for f in ['001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql']:db.execute((ROOT/'migrations'/f).read_text(encoding='utf8'))
  os.environ.update(LABAN_BROWSER_TEST_DATABASE=pg.url,ADVISOR_CONTROLLED_ROLLOUT='true',ADVISOR_TEST_UIDS='no-browser-role',ADVISOR_PROFILE_ENABLED='false')
  h.checks=checks;h.main()
