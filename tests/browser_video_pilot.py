"""Chrome + YouTube LIVE. Chỉ đọc thư viện/Preview, không Firebase/AI/database.

python tests/browser_video_pilot.py --origin https://DEPLOYMENT.vercel.app --protected
Phát sau thao tác kiểm thử chủ động, không giả lập player hoặc onStateChange.
"""
import argparse,asyncio,base64,json,os,re,subprocess,sys,time,urllib.request
from pathlib import Path
import httpx,websockets
from browser_smoke import Browser

ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'artifacts';ART.mkdir(exist_ok=True)
PILOT=('ky-su-du-lieu','dieu-duong','giao-vien','ky-su-xay-dung','dau-bep')
INIT="""window.videoAudit={};window.auditRequests=[];const f=fetch;window.fetch=(u,o={})=>{auditRequests.push({path:String(u).split('?')[0],method:o.method||'GET'});return f(u,o)};
window.onYouTubeIframeAPIReady=()=>{const Original=YT.Player;YT.Player=function(slot,options){const e=options.events;options.events={...e,onReady:x=>{window.actualPlayer=x.target;videoAudit.ready=true;e.onReady?.(x)},onError:x=>{videoAudit.error=x.data;e.onError?.(x)},onStateChange:x=>{videoAudit.state=x.data;e.onStateChange?.(x)}};return new Original(slot,options)}};"""

async def checks(wsurl,origin,cookies):
 report={'origin':origin,'browser':'real Chrome','youtube':'real IFrame API, no mock','checks':{},'playback':[]}
 def passed(key):report['checks'][key]='PASS';save();print('PASS '+key,flush=True)
 def save():(ART/'video-pilot-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 async with websockets.connect(wsurl,origin='http://localhost:9273',max_size=20000000) as ws:
  b=Browser(ws)
  for m in ('Runtime.enable','Page.enable','Network.enable'):await b.call(m)
  await b.call('Page.addScriptToEvaluateOnNewDocument',{'source':INIT})
  for name,value in cookies:await b.call('Network.setCookie',{'name':name,'value':value,'url':origin,'secure':True,'httpOnly':True,'sameSite':'Lax'})
  async def wait(expr,seconds=35):
   for _ in range(int(seconds/.2)):
    if await b.evaluate('Boolean('+expr+')'):return
    await asyncio.sleep(.2)
   raise AssertionError('BROWSER_WAIT_FAILED')
  async def click(selector):await b.call('Runtime.evaluate',{'expression':f'document.querySelector({json.dumps(selector)}).click()','userGesture':True})
  async def shot(name):
   v=await b.call('Page.captureScreenshot',{'format':'png'});(ART/name).write_bytes(base64.b64decode(v['data']))
  await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
  await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec'});await wait("document.querySelectorAll('.story-card').length===12")
  assert await b.evaluate("document.querySelector('#story-count').textContent.includes('200 nghề')&&document.querySelector('#story-count').textContent.includes('7 nghề có video')&&document.querySelector('#story-count').textContent.includes('193 chưa có video')")
  assert await b.evaluate("!document.querySelector('a a')&&!document.querySelector('iframe')&&!document.querySelector('script[src*=youtube]')")
  assert await b.evaluate("[...document.querySelectorAll('.story-card:has(.story-open-video)')].every(c=>c.querySelector('.story-open-comic')&&new URL(c.querySelector('.story-open-video').href).searchParams.get('tab')==='video'&&new URL(c.querySelector('.story-open-comic').href).searchParams.get('tab')==='comic')")
  await wait("[...document.querySelectorAll('#story-grid img')].every(i=>i.getBoundingClientRect().top>=innerHeight||(i.complete&&i.naturalWidth>0))")
  await shot('video-pilot-library-desktop.png');passed('library_200_7_video_193_missing_two_distinct_links_no_lazy_player')
  for cid in PILOT:
   await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe='+cid+'&tab=video'});await wait("document.querySelector('#video-content')?.hidden===false")
   assert await b.evaluate("document.querySelector('#tab-video').textContent.includes('Xem video')&&document.querySelector('#tab-comic').textContent.includes('Đọc truyện')&&!document.querySelector('iframe')")
   expected=await b.evaluate("new URL(document.querySelector('#youtube-link').href).searchParams.get('v')")
   await click('#play-video');await wait('videoAudit.ready||videoAudit.error')
   assert not await b.evaluate('videoAudit.error??null'),'YOUTUBE_EMBED_ERROR'
   await b.call('Runtime.evaluate',{'expression':'actualPlayer.mute();actualPlayer.playVideo()','userGesture':True})
   await wait('actualPlayer.getPlayerState()===1&&actualPlayer.getCurrentTime()>2',35)
   start=await b.evaluate('actualPlayer.getCurrentTime()');await asyncio.sleep(1.4);end=await b.evaluate('actualPlayer.getCurrentTime()');assert end>start+.7
   assert await b.evaluate('actualPlayer.getVideoData().video_id')==expected
   report['playback'].append({'career_id':cid,'video_id':expected,'state':1,'time_start':round(start,2),'time_end':round(end,2),'status':'PASS'});save()
   if cid=='dau-bep':await shot('video-pilot-playing-desktop.png')
   await click('#tab-comic');assert await b.evaluate("!document.querySelector('#comic-panel').hidden&&!document.querySelector('#youtube-host iframe')&&document.querySelector('#scene-art svg')!==null")
   await click('#next-scene');assert await b.evaluate("document.querySelector('#reading-progress').value>0")
   assert not await b.evaluate("auditRequests.some(r=>r.method!=='GET')")
   passed(cid+'_plays_real_correct_video_and_comic_survives_no_ai')
  # Missing is not a failed player: no video source is attached to Data Scientist.
  await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=nha-khoa-hoc-du-lieu&tab=video'});await wait("document.querySelector('#video-empty')?.hidden===false")
  assert await b.evaluate("document.querySelector('#video-content').hidden&&!document.querySelector('iframe')&&document.querySelector('#video-empty').textContent.includes('chưa được gắn')")
  await click('#tab-comic');assert await b.evaluate("!document.querySelector('#comic-panel').hidden");passed('missing_video_distinct_from_playback_error_story_still_available')
  await b.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
  await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?q=K%E1%BB%B9%20s%C6%B0%20d%E1%BB%AF%20li%E1%BB%87u'});await wait("document.querySelectorAll('.story-card').length===1")
  assert await b.evaluate("document.documentElement.scrollWidth<=innerWidth+1&&document.querySelector('.story-open-video').getBoundingClientRect().height>=44&&document.querySelector('.story-open-comic').getBoundingClientRect().height>=44")
  await wait("document.querySelector('#story-grid img').complete&&document.querySelector('#story-grid img').naturalWidth>0")
  await b.evaluate("document.querySelector('.story-card').scrollIntoView({block:'center'})")
  await shot('video-pilot-library-mobile.png');await click('.story-open-comic');await wait("document.querySelector('#story-detail')?.hidden===false");assert await b.evaluate("document.querySelector('#tab-comic').getAttribute('aria-selected')==='true'")
  await shot('video-pilot-comic-mobile.png');await b.evaluate('history.back()');await wait("document.querySelectorAll('.story-card').length===1&&!document.querySelector('#story-library').hidden");await b.evaluate('history.forward()');await wait("document.querySelector('#story-detail')?.hidden===false");assert await b.evaluate("document.querySelector('#tab-comic').getAttribute('aria-selected')==='true'")
  assert len([t for t in (await b.call('Target.getTargets'))['targetInfos'] if t['type']=='page'])==1
  assert not b.errors;passed('mobile_touch_targets_back_forward_one_tab_zero_js_errors');report['status']='PASS';save()

def main():
 p=argparse.ArgumentParser();p.add_argument('--origin',required=True);p.add_argument('--protected',action='store_true');args=p.parse_args();origin=args.origin.rstrip('/');cookies=[]
 if args.protected:
  c=subprocess.run(['npx.cmd','vercel@65.4.0','curl','/api/health','--deployment',origin,'--scope','khkt3','--','--silent','--include','--max-time','30','--header','x-vercel-set-bypass-cookie: true'],cwd=ROOT,capture_output=True,text=True,encoding='utf8',timeout=75);assert c.returncode==0,'VERCEL_ACCESS_FAILED'
  cookies=[tuple(pair.split('=',1)) for pair in re.findall(r'^set-cookie:\s*([^;\r\n]+)',c.stdout,re.I|re.M) if pair.startswith(('_vercel','__vercel'))]
 chrome=subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe','--headless=new','--incognito','--disable-gpu','--no-first-run','--no-proxy-server','--remote-debugging-port=9273','--remote-allow-origins=http://localhost:9273','--user-data-dir='+str(ART/('chrome-video-preview-'+str(time.time_ns()))),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  for _ in range(100):
   try:
    with urllib.request.urlopen('http://localhost:9273/json',timeout=1) as r:tabs=[t for t in json.load(r) if t.get('type')=='page']
    if tabs:break
   except OSError:time.sleep(.1)
  asyncio.run(checks(tabs[0]['webSocketDebuggerUrl'],origin,cookies))
 finally:chrome.terminate();chrome.wait(timeout=10)
if __name__=='__main__':main()
