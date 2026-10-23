"""Cookie guest + legacy transport proof: isolated local PG/provider fixtures only."""
import json
import os
import psycopg
import websockets
import browser_smoke as h
from postgres_fixture import LocalPostgres

OUT=h.ROOT/'artifacts'/'qa'
ROWS=[]


async def checks(url, origin):
    async with websockets.connect(url,origin='http://localhost:9227',max_size=30000000) as socket:
        b=h.Browser(socket)
        await b.call('Runtime.enable');await b.call('Page.enable');await b.call('Network.enable')
        async def run(code):
            return await b.evaluate('(async()=>{'+code+'})()')
        async def check(name,expression):
            actual=await b.evaluate('(async()=>('+expression+'))()')
            ROWS.append({'id':name,'status':'PASS' if actual is True else 'FAIL','actual':actual})
            (OUT/'shared-browser-proof.json').write_text(json.dumps(ROWS,ensure_ascii=False,indent=2),encoding='utf8')
        await b.call('Page.addScriptToEvaluateOnNewDocument',{'source':r'''
window.proof={calls:[]};const originalFetch=fetch;
window.fetch=async(url,options={})=>{let r=await originalFetch(url,options);
proof.calls.push({path:new URL(url,location.href).pathname,status:r.status,bearer:Boolean(options.headers?.Authorization)});return r;};
'''})
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?fixture_no_firebase=1'})
        await b.wait_for("!document.querySelector('#career-survey').hidden&&!document.querySelector('#survey-next').disabled")
        await run("window.identityProof=await (await fetch('/api/auth/me')).json();window.firstUID=identityProof.user.uid")
        await check('cookie.SDK-unavailable-server-verified-guest',"identityProof.user.server_guest===true&&identityProof.user.provider==='anonymous'&&!proof.calls.some(x=>x.bearer)")
        cookies=(await b.call('Network.getCookies',{'urls':[origin]}))['cookies']
        cookie=next(c for c in cookies if c['name']=='laban_guest')
        # Do not write cookie values into artifacts or logs.
        await check('cookie.HttpOnly-SameSite',json.dumps(cookie['httpOnly'] and cookie['sameSite']=='Strict'))
        for _ in range(5):await b.evaluate("document.querySelector('#survey-answer').value='Vẽ và tìm hiểu máy tính';document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===3")
        await b.evaluate("sessionStorage.setItem('__proof_uid',firstUID)")
        await b.call('Page.reload')
        await b.wait_for("document.querySelectorAll('.message-row').length===3")
        await check('cookie.reload-UID-quota-survey-history',"(await (await fetch('/api/auth/me')).json()).user.uid===sessionStorage.getItem('__proof_uid')&&(await (await fetch('/api/ai/config')).json()).guest_quota.used_questions===1&&document.querySelector('#career-survey').hidden")
        await b.call('Page.navigate',{'url':origin+'/?fixture_no_firebase=1'})
        await run("window.access=await import('/assets/ai-access.js');window.legacy=await (await fetch('/api/advice',{method:'POST',headers:await access.aiHeaders(),body:JSON.stringify({question:'Em thích vẽ',request_id:crypto.randomUUID()})})).json()")
        await check('legacy.advice-cookie-transport',"legacy.answer.includes('BẢN DEMO')&&legacy.guest_quota.used_questions===2&&proof.calls.some(x=>x.path==='/api/advice'&&x.status===200&&!x.bearer)")
        await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=bac-si&fixture_no_firebase=1'})
        await b.wait_for("!document.querySelector('#story-content').hidden")
        await b.evaluate("document.querySelector('#story-question').value='Em cần kỹ năng gì?';document.querySelector('#story-ask-form').requestSubmit()")
        await b.wait_for("document.querySelector('#story-answer').textContent.includes('BẢN DEMO')")
        await check('legacy.story-form-cookie-transport',"proof.calls.some(x=>x.path==='/api/career-stories/bac-si/ask'&&x.status===200&&!x.bearer)")
        await run("window.access=await import('/assets/ai-access.js');for(let i=0;i<5;i++){let r=await fetch('/api/advice',{method:'POST',headers:await access.aiHeaders(),body:JSON.stringify({question:'Nghề sáng tạo nào?',request_id:crypto.randomUUID()})});if(!r.ok)throw new Error('unexpected quota');}")
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?fixture_no_firebase=1'})
        await b.wait_for("document.querySelector('#guest-banner').classList.contains('limit-reached')")
        await check('cookie.eighth-question-login-link-no-forced-login',"!document.querySelector('#guest-banner').hidden&&document.querySelector('#guest-login').getAttribute('href').includes('login=1')")
        await b.screenshot('qa/shared-cookie-limit.png')
        await b.call('Page.navigate',{'url':origin+'/'})
        await b.evaluate("sessionStorage.setItem('__fixture_login','1')")
        await b.call('Page.reload')
        await run("window.access=await import('/assets/ai-access.js');window.member=await (await fetch('/api/advice',{method:'POST',headers:await access.aiHeaders(),body:JSON.stringify({question:'Em thích vẽ',request_id:crypto.randomUUID()})})).json()")
        await check('legacy.member-token-transport',"member.answer.includes('BẢN DEMO')&&member.guest_quota===null&&proof.calls.some(x=>x.path==='/api/advice'&&x.status===200&&x.bearer)")
        await check('browser.runtime-exceptions',json.dumps(not b.errors))
        print(json.dumps({'PASS':sum(r['status']=='PASS' for r in ROWS),'FAIL':sum(r['status']=='FAIL' for r in ROWS)},ensure_ascii=True))


if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    with LocalPostgres() as pg:
        with psycopg.connect(pg.url,autocommit=True) as db:
            for name in ('001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql'):
                db.execute((h.ROOT/'migrations'/name).read_text(encoding='utf8'))
        os.environ.update(LABAN_BROWSER_TEST_DATABASE=pg.url,LABAN_BROWSER_TEST_LEGACY_AI='1',DEEPSEEK_API_KEY='browser-fixture-only')
        h.checks=checks;h.main()
