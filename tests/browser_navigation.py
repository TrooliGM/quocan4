"""Real Chrome/DOM for navigation security, tab behavior and auth-return helpers.

Local static fixture only; does not prove Firebase popup or model intelligence.
"""
import asyncio
import json
import subprocess
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import websockets
from browser_smoke import Browser

ROOT=Path(__file__).resolve().parents[1]
POSTS=[]
class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def handle(self):
        try:super().handle()
        except ConnectionResetError:pass
    def do_POST(self):POSTS.append(self.path);self.send_error(400)
    def do_GET(self):
        if self.path=='/fixture':
            body='''<!doctype html><meta charset="utf-8"><title>Navigation fixture</title><div id="result"></div>
            <script type="module">
            import {navigationButtons,navigationPath,keepVerifiedCitations} from '/public/assets/navigation-actions.js';
            import {beginLogin,loginDestination,finishLogin,safeReturnPath} from '/public/assets/chat-journey.js';
            window.clicked=0;window.attacked=0;
            window.harness={navigationButtons,navigationPath,keepVerifiedCitations,beginLogin,loginDestination,finishLogin,safeReturnPath};
            sessionStorage.setItem('fixture-draft','nội dung khảo sát và tin nhắn');
            window.ready=true;
            </script>'''.encode()
        elif self.path.startswith('/?career=') or self.path.startswith('/mot-ngay-lam-viec'):
            body=b'<!doctype html><title>Destination fixture</title>'
        else:return super().do_GET()
        self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(body)

async def run(socket_url,origin):
    async with websockets.connect(socket_url,origin='http://localhost:9236',max_size=20000000) as ws:
        b=Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
        await b.call('Page.navigate',{'url':origin+'/fixture'})
        for _ in range(100):
            if await b.evaluate('window.ready===true'):break
            await asyncio.sleep(.1)
        assert await b.evaluate('window.ready===true')
        for path in ['//evil.test','/\\evil.test','/ai-career-advisor?return_to=https://evil.test','https://evil.test','/other']:
            got=await b.evaluate('harness.safeReturnPath('+json.dumps(path)+')')
            assert got=='/' or got=='/ai-career-advisor' # Unknown return_to cannot be retained.
        for path in ['/?career=lap-trinh#careers','/mot-ngay-lam-viec?nghe=lap-trinh',
                     '/ai-career-advisor?mode=career_exploration&career_id=lap-trinh&conversation=11111111-2222-3333-4444-555555555555']:
            assert await b.evaluate('(harness.beginLogin('+json.dumps(path)+'),harness.finishLogin())')==path
        items=[{'kind':'career_profile','career_id':'lap-trinh','label':'<img src=x onerror="window.attacked=1">','href':'/?career=lap-trinh#careers'},
               {'kind':'career_story','career_id':None,'label':'Thư viện Truyện nghề','href':'/mot-ngay-lam-viec'},
               {'kind':'career_story','career_id':None,'label':'Mở trang ngoài','href':'//evil.test'},
               {'kind':'career_story','career_id':'%2f%2fevil.test','label':'Mở trang ngoài','href':'/mot-ngay-lam-viec?nghe=%2f%2fevil.test'}]
        assert await b.evaluate("(()=>{const el=harness.navigationButtons("+json.dumps(items)+",()=>window.clicked++);document.querySelector('#result').append(el);return el.querySelectorAll('a').length})()") == 2
        assert await b.evaluate("document.querySelectorAll('#result img, #result script').length===0 && window.attacked===0")
        assert await b.evaluate("[...document.querySelectorAll('#result a')].every(a=>a.target==='_blank'&&a.rel.includes('noopener'))")
        assert await b.evaluate("""(()=>{const box=document.createElement('div');
        box.innerHTML='<a href="//evil.test">ngoài</a><a href="/?career=unknown">tự tạo</a><a href="https://example.gov.vn/report">nguồn</a>';
        harness.keepVerifiedCitations(box,[{url:'https://example.gov.vn/report'}]);
        return box.querySelectorAll('a').length===1&&box.querySelector('a').rel.includes('noopener')&&box.textContent==='ngoàitự tạonguồn';})()""")
        for width in [1440,390]:
            await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':844,'deviceScaleFactor':1,'mobile':width<500})
            assert await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        await b.call('Runtime.evaluate',{'expression':"document.querySelector('#result a').click()",'userGesture':True})
        await asyncio.sleep(.5)
        targets=(await b.call('Target.getTargets'))['targetInfos']
        new=[t for t in targets if t.get('url')==origin+'/?career=lap-trinh#careers']
        assert new and await b.evaluate("location.pathname==='/fixture'&&window.clicked===1&&sessionStorage.getItem('fixture-draft')==='nội dung khảo sát và tin nhắn'")
        assert not POSTS
        await b.call('Target.closeTarget',{'targetId':new[0]['targetId']})
        return {'dom_xss_open_redirect':'PASS','same_tab_draft':'PASS','new_tab_route':'PASS','zero_ai_requests':'PASS static fixture POST count0','auth_return_paths':'PASS local helpers, not Google popup','desktop_mobile_overflow':'PASS'}

if __name__=='__main__':
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start();origin='http://127.0.0.1:'+str(server.server_port)
    artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True)
    p=subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe','--headless=new','--no-first-run','--no-proxy-server','--remote-debugging-port=9237','--remote-allow-origins=http://localhost:9236','--user-data-dir='+str(artifacts/('chrome-nav-'+str(time.time_ns()))),'about:blank'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for _ in range(100):
            try:
                with urllib.request.urlopen('http://localhost:9237/json',timeout=1) as r:tabs=[t for t in json.load(r) if t.get('type')=='page']
                if tabs:break
            except OSError:time.sleep(.1)
        report=asyncio.run(run(tabs[0]['webSocketDebuggerUrl'],origin));print(json.dumps(report))
        (artifacts/'task43-browser-local.json').write_text(json.dumps(report,indent=2))
    finally:p.terminate();p.wait(timeout=10);server.shutdown()
