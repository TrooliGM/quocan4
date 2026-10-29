"""Phát nhúng LIVE trong Chrome, lưu chứng cứ theo video. Không tự công bố.

python scripts/check_video_playback.py --workers 3
Không tải/rehost video; chỉ điều khiển iframe YouTube thật sau thao tác phát.
"""
import argparse,asyncio,base64,http.server,json,os,subprocess,sys,threading,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
import httpx,websockets
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tests'),str(R),str(R/'scripts')]
from browser_smoke import Browser
from career_videos import videos
from inspect_career_video_candidates import inspect
ART=R/'artifacts/video-research';ART.mkdir(parents=True,exist_ok=True)
PROOF=R/'docs/video-research/playback.json'
HTML='''<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#f3f1e9;font:15px sans-serif}h1{font-size:16px;margin:12px}#host{width:960px;height:540px}iframe{width:100%;height:100%}</style><h1 id="title">Kiểm tra video nghề nghiệp LIVE</h1><button id="play">Phát video kiểm thử</button><div id="host"></div><script type="module">
import {YouTubePlayer} from '/assets/youtube-player.js';window.evidence={};
window.onYouTubeIframeAPIReady=()=>{const Original=YT.Player;YT.Player=function(slot,options){const e=options.events;options.events={...e,onReady:x=>{window.actualPlayer=x.target;evidence.ready=true;e.onReady?.(x)},onError:x=>{evidence.error=x.data;e.onError?.(x)},onStateChange:x=>{evidence.state=x.data;e.onStateChange?.(x)}};return new Original(slot,options)}};
window.player=new YouTubePlayer(document.querySelector('#host'),message=>evidence.failure=message);document.querySelector('#play').onclick=()=>player.open(video);
</script>'''.encode()
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  body=HTML if self.path=='/' else (R/'public/assets/youtube-player.js').read_bytes() if self.path=='/assets/youtube-player.js' else None
  self.send_response(200 if body else 404);self.send_header('Content-Type','text/html; charset=utf-8' if self.path=='/' else 'text/javascript; charset=utf-8');self.end_headers()
  if body:self.wfile.write(body)
 def log_message(self,*a):pass

async def child_eval(b,sid,expression):
 b.sequence+=1;n=b.sequence
 await b.socket.send(json.dumps({'id':n,'method':'Runtime.evaluate','sessionId':sid,'params':{'expression':expression,'returnByValue':True}}))
 while True:
  event=json.loads(await b.socket.recv())
  if event.get('id')==n:return event.get('result',{}).get('result',{}).get('value')

async def audit(b,origin,cid,key,meta):
 result={'career_id':cid,'video_id':key,'url':'https://www.youtube.com/watch?v='+key,'checked_at':datetime.now(timezone.utc).isoformat(),'status':'UNVERIFIED','samples':[]}
 if meta.get('playability',{}).get('status')!='OK' or meta.get('family_safe') is not True:
  return {**result,'status':'METADATA_NOT_PLAYABLE_OR_AGE_UNVERIFIED','metadata_status':meta.get('playability',{}).get('status')}
 await b.call('Page.navigate',{'url':origin})
 for _ in range(100):
  if await b.evaluate('Boolean(window.player)'):break
  await asyncio.sleep(.1)
 await b.evaluate('window.video='+json.dumps({'youtube_video_id':key,'title':meta['title'],'embeddable':True})+';document.querySelector("#title").textContent='+json.dumps(cid+' · '+meta['title']))
 await b.call('Runtime.evaluate',{'expression':'document.querySelector("#play").click()','userGesture':True})
 for _ in range(85):
  if await b.evaluate('Boolean(evidence.ready||evidence.error||evidence.failure)'):break
  await asyncio.sleep(.2)
 evidence=await b.evaluate('({...evidence})');result.update({k:v for k,v in evidence.items() if k in ('ready','error','failure')})
 if evidence.get('error'):return {**result,'status':'EMBED_ERROR'}
 if not evidence.get('ready'):return {**result,'status':'PLAYER_NOT_READY'}
 await b.call('Runtime.evaluate',{'expression':'actualPlayer.mute();actualPlayer.playVideo();actualPlayer.loadModule("captions")','userGesture':True})
 for _ in range(300):
  if await b.evaluate('Boolean(evidence.error)||actualPlayer.getPlayerState()===1&&actualPlayer.getCurrentTime()>2'):break
  await asyncio.sleep(.15)
 current=await b.evaluate('({time:actualPlayer.getCurrentTime(),state:actualPlayer.getPlayerState(),error:evidence.error??null,video_id:actualPlayer.getVideoData().video_id})');result.update(current)
 if current.get('error'):return {**result,'status':'EMBED_ERROR'}
 if current['state']!=1 or current['time']<2 or current['video_id']!=key:return {**result,'status':'PLAYBACK_NOT_CONFIRMED'}
 await asyncio.sleep(1.2);result['time_end']=await b.evaluate('actualPlayer.getCurrentTime()')
 if result['time_end']<=current['time']+.6:return {**result,'status':'CLOCK_NOT_ADVANCING'}
 result['status']='PASS';child=None
 try:
  frames=(await b.call('Target.getTargets'))['targetInfos'];frame=next((f for f in frames if f['type']=='iframe' and '/embed/'+key in f.get('url','')),None)
  if frame:child=(await b.call('Target.attachToTarget',{'targetId':frame['targetId'],'flatten':True}))['sessionId']
 except Exception:pass
 languages=meta.get('caption_languages',[])
 if languages:
  lang='vi' if 'vi' in languages else 'en' if 'en' in languages else languages[0]
  try:await b.evaluate('actualPlayer.setOption("captions","track",{languageCode:'+json.dumps(lang)+'})')
  except Exception:pass
 # Observe one early frame and one middle frame; store actual seek time, never infer it.
 for i,fraction in enumerate((None,.45)):
  target=None if fraction is None else max(5,int(int(meta.get('duration') or 0)*fraction))
  if target:
   await b.call('Runtime.evaluate',{'expression':f'actualPlayer.seekTo({target},true);actualPlayer.playVideo()','userGesture':True})
   for _ in range(30):
    if await b.evaluate(f'Math.abs(actualPlayer.getCurrentTime()-{target})<4&&actualPlayer.getPlayerState()===1'):break
    await asyncio.sleep(.2)
  await asyncio.sleep(.7);actual=await b.evaluate('actualPlayer.getCurrentTime()');text=''
  if child:
   try:text=await child_eval(b,child,'[...document.querySelectorAll(".ytp-caption-segment")].map(n=>n.textContent).join(" ")') or ''
   except Exception:pass
  shot=await b.call('Page.captureScreenshot',{'format':'jpeg','quality':76});name=key+'-'+str(i)+'.jpg';(ART/name).write_bytes(base64.b64decode(shot['data']))
  result['samples'].append({'file':'artifacts/video-research/'+name,'requested_time':target,'actual_time':round(actual,2),'seek_reached':target is None or abs(actual-target)<4,'caption_text':str(text)[:1000]})
 if child:
  try:await b.call('Target.detachFromTarget',{'sessionId':child})
  except Exception:pass
 return result

async def run(tabs,origin,jobs,proof):
 queue=asyncio.Queue()
 for job in jobs:queue.put_nowait(job)
 lock=asyncio.Lock();done=0
 async def worker(url):
  nonlocal done
  async with websockets.connect(url,origin='http://localhost:9275',max_size=20000000) as ws:
   b=Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable');await b.call('Emulation.setDeviceMetricsOverride',{'width':980,'height':630,'deviceScaleFactor':1,'mobile':False})
   while not queue.empty():
    try:cid,key,meta=queue.get_nowait()
    except asyncio.QueueEmpty:break
    try:result=await audit(b,origin,cid,key,meta)
    except Exception as e:result={'career_id':cid,'video_id':key,'status':'AUDIT_ERROR','error_type':type(e).__name__}
    async with lock:
     proof[key]=result;tmp=PROOF.with_suffix('.tmp');tmp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(PROOF);done+=1
     print(json.dumps({'done':done,'total_this_run':len(jobs),'career_id':cid,'status':result['status'],'remaining':queue.qsize()}),flush=True)
 await asyncio.gather(*(worker(t['webSocketDebuggerUrl']) for t in tabs))

def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=3,choices=[1,2,3]);p.add_argument('--limit',type=int);a=p.parse_args();short=json.loads((R/'docs/video-research/shortlist.json').read_text(encoding='utf8'))['choices'];proof=json.loads(PROOF.read_text(encoding='utf8')) if PROOF.exists() else {}
 for v in videos():
  if v.verification_status=='verified':short.setdefault(v.career_id,v.youtube_video_id)
 jobs=[]
 for cid,key in short.items():
  if key not in proof:
   meta=inspect(key);jobs.append((cid,key,meta))
 if a.limit:jobs=jobs[:a.limit]
 if not jobs:print('No unchecked shortlisted videos.');return
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start();origin='http://127.0.0.1:'+str(server.server_port)
 proc=subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe','--headless=new','--incognito','--disable-gpu','--no-first-run','--no-proxy-server','--disable-background-timer-throttling','--disable-renderer-backgrounding','--remote-debugging-port=9275','--remote-allow-origins=http://localhost:9275','--user-data-dir='+str(ART/('chrome-bulk-'+str(time.time_ns()))),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
 try:
  for _ in range(100):
   try:
    with urllib.request.urlopen('http://localhost:9275/json',timeout=1) as r:tabs=[t for t in json.load(r) if t.get('type')=='page']
    if tabs:break
   except OSError:time.sleep(.1)
  while len(tabs)<a.workers:
   tabs.append(httpx.put('http://localhost:9275/json/new?about:blank',timeout=5).json())
  asyncio.run(run(tabs,origin,jobs,proof))
 finally:proc.terminate();proc.wait(timeout=10);server.shutdown()
if __name__=='__main__':main()
