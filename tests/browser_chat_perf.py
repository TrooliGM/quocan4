"""UI/network measurements, no AI calls. Production guest or isolated fixture member."""
import asyncio,json,os,subprocess,sys,time
from pathlib import Path
import urllib.request
import websockets
import browser_smoke as h
ROOT=Path(__file__).resolve().parents[1]
INIT=r'''
window.perfChat={requests:[],marks:[],long_tasks:[]};
try{new PerformanceObserver(list=>{for(const entry of list.getEntries())perfChat.long_tasks.push(entry.duration);}).observe({type:'longtask',buffered:true});}catch{}
const nativeFetch=window.fetch;
window.fetch=async(...args)=>{const path=String(args[0]),method=args[1]?.method||'GET',start=performance.now();try{
const r=await nativeFetch(...args);if(path.startsWith('/api/')){const op=path==='/api/ai/chat'?'AI':path==='/api/ai/sessions'?(method==='POST'?'create':'list'):path.startsWith('/api/ai/sessions/')?'open':'other';perfChat.requests.push({op,method,ms:performance.now()-start,http:r.status});}return r;}catch(e){if(e.name!=='AbortError')perfChat.requests.push({op:'error',ms:performance.now()-start});throw e;}};
window.startProbe=(kind,index)=>{const start=performance.now();const mark={kind,feedback:null,content:null,ready:null};perfChat.marks.push(mark);
const observe=()=>{const surveying=document.querySelector('#career-survey')?.hidden===false,notice=document.querySelector('#chat-notice')?.hidden===false;
const selected=[...document.querySelectorAll('.history-item')].findIndex(x=>x.classList.contains('active'))===index;
if(mark.feedback===null && (kind==='create'?(notice||document.querySelector('#start-chat')?.disabled):selected)){mark.feedback=performance.now()-start;requestAnimationFrame(()=>{mark.visual_frame=performance.now()-start;});}
if(mark.content===null && surveying && (kind==='create'||selected))mark.content=performance.now()-start;
if(surveying && !document.querySelector('#survey-next')?.disabled && (kind==='create'||selected)){mark.ready=performance.now()-start;o.disconnect();}};
const o=new MutationObserver(observe);o.observe(document.body,{subtree:true,attributes:true,childList:true});
document.querySelector(kind==='create'?'#start-chat':'.history-open:nth-child(1)');
if(kind==='create')document.querySelector('#start-chat').click();else document.querySelectorAll('.history-open')[index].click();observe();};
'''
async def checks(wsurl,origin):
    async with websockets.connect(wsurl,origin='http://localhost:9227',max_size=20000000) as ws:
        b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
        await b.call('Page.addScriptToEvaluateOnNewDocument',{'source':INIT})
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor'})
        await b.wait_for("document.querySelector('#chat-app')?.hidden===false && !document.querySelector('#start-chat').disabled",timeout=90)
        if '--member' in sys.argv:
            await b.evaluate("sessionStorage.setItem('__fixture_login','1')");await b.call('Page.reload')
            await b.wait_for("document.querySelector('#chat-app')?.hidden===false && !document.querySelector('#start-chat').disabled",timeout=90)
        for i in range(5):
            await b.evaluate("document.querySelector('#new-chat').click();startProbe('create',-1)")
            await b.wait_for(f"perfChat.marks.length==={i+1} && perfChat.marks.at(-1).ready!==null",timeout=60)
            await b.evaluate(f"document.querySelector('#survey-answer').value='draft-{i}';document.querySelector('#survey-answer').dispatchEvent(new Event('input'))")
        for i,index in enumerate([4,3,2,1,0]):
            await b.evaluate(f"startProbe('open',{index})")
            await b.wait_for(f"perfChat.marks.length==={i+6} && perfChat.marks.at(-1).ready!==null",timeout=60)
        report=await b.evaluate('perfChat');assert not any(r['op']=='AI' for r in report['requests'])
        if '--stress' in sys.argv:
            await b.evaluate("window.realDateNow=Date.now;Date.now=()=>realDateNow()+60000;perfChat.requests=[]")
            await b.evaluate("window.nativeDelayedFetch=fetch;fetch=async(...args)=>{const r=await nativeDelayedFetch(...args);if(String(args[0]).startsWith('/api/ai/sessions/'))await new Promise(ok=>setTimeout(ok,250));return r;}")
            expected=await b.evaluate("document.querySelectorAll('.history-open')[0].dataset.sessionId")
            await b.evaluate("(async()=>{for(const i of [4,3,2,1,0]){document.querySelectorAll('.history-open')[i].click();await new Promise(r=>setTimeout(r,15));}})()")
            await b.wait_for("!document.querySelector('#survey-next').disabled && document.querySelector('.history-open[aria-current=true]')?.dataset.sessionId==="+json.dumps(expected))
            await asyncio.sleep(.5)
            assert await b.evaluate("document.querySelector('.history-open[aria-current=true]')?.dataset.sessionId==="+json.dumps(expected))
            assert await b.evaluate("document.querySelector('#survey-answer').value==='draft-4'")
            await b.evaluate("perfChat.requests=[];document.querySelectorAll('.history-open')[1].click();document.querySelectorAll('.history-open')[1].click()")
            await b.wait_for("!document.querySelector('#survey-next').disabled")
            assert await b.evaluate("perfChat.requests.filter(x=>x.op==='open').length===1")
            report['rapid_last_response_wins']=True;report['duplicate_open_single_request']=True
        label=sys.argv[1];report.update(label=label,identity='member fixture' if '--member' in sys.argv else 'real server guest',ai_calls=0)
        out=ROOT/'artifacts/perf';out.mkdir(exist_ok=True,parents=True);(out/(label+'-browser.json')).write_text(json.dumps(report,indent=2),encoding='utf8')
        print(json.dumps({'label':label,'marks':report['marks'],'requests':len(report['requests']),'ai_calls':0}),flush=True)
if __name__=='__main__':
    if '--production' in sys.argv:
        chrome=Path('C:/Program Files/Google/Chrome/Application/chrome.exe');out=ROOT/'artifacts/perf';out.mkdir(exist_ok=True,parents=True)
        with (out/'browser.log').open('w',encoding='utf8') as log:
            proc=subprocess.Popen([str(chrome),'--headless=new','--disable-gpu','--no-first-run','--no-proxy-server','--remote-debugging-port=9227','--remote-allow-origins=http://localhost:9227','--user-data-dir='+str(out/('chrome-'+str(time.time_ns()))),'about:blank'],stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
            try:
                for _ in range(100):
                    try:
                        with urllib.request.urlopen('http://localhost:9227/json',timeout=1) as r:tabs=json.load(r)
                        if tabs:break
                    except OSError:time.sleep(.1)
                asyncio.run(checks(next(t['webSocketDebuggerUrl'] for t in tabs if t['type']=='page'),'https://labanhuongnghiep.vercel.app'))
            finally:proc.terminate();proc.wait(timeout=10)
    else:
        from postgres_fixture import LocalPostgres
        import psycopg
        os.environ['LABAN_TEST_PG_BIN']='D:/khkt/artifacts/postgres-tools/pgsql/bin'
        with LocalPostgres() as pg:
            with psycopg.connect(pg.url,autocommit=True) as db:
                for f in ['001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql']:db.execute((ROOT/'migrations'/f).read_text(encoding='utf8'))
            os.environ['LABAN_BROWSER_TEST_DATABASE']=pg.url;h.checks=checks;h.main()
