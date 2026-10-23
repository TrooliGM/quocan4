"""Task 1+2 functional regression, isolated PostgreSQL/Firebase stub/AI demo only."""
import asyncio,json,os,time
from pathlib import Path
import psycopg,websockets
import browser_smoke as h
from postgres_fixture import LocalPostgres

OUT=h.ROOT/'artifacts'/'qa'
ROWS=[]
CONSOLE_ERRORS=[]
REQUEST_ERRORS=[]
class Browser(h.Browser):
    async def call(self,method,params=None):
        self.sequence+=1;identifier=self.sequence
        await self.socket.send(json.dumps({'id':identifier,'method':method,'params':params or {}}))
        while True:
            msg=json.loads(await self.socket.recv());kind=msg.get('method');p=msg.get('params',{})
            if kind=='Runtime.exceptionThrown':self.errors.append(p['exceptionDetails'])
            if kind=='Runtime.consoleAPICalled' and p.get('type')=='error':CONSOLE_ERRORS.append(p)
            if kind=='Network.responseReceived' and p['response']['status']>=400:
                REQUEST_ERRORS.append({'url':p['response']['url'],'status':p['response']['status']})
            if kind=='Network.loadingFailed' and not p.get('canceled'):REQUEST_ERRORS.append({'type':p.get('type'),'error':p.get('errorText')})
            if msg.get('id')==identifier:
                if 'error' in msg:raise RuntimeError(msg['error'])
                return msg.get('result',{})
async def checks(url,origin):
    async with websockets.connect(url,origin='http://localhost:9227',max_size=30000000) as socket:
        b=Browser(socket)
        await b.call('Runtime.enable');await b.call('Page.enable');await b.call('Network.enable')
        await b.call('Page.addScriptToEvaluateOnNewDocument',{'source':r"""
window.qa={requests:[],modalHold:null,listHold:null};const nativeFetch=fetch;
window.fetch=async(input,opts={})=>{let u=new URL(typeof input==='string'?input:input.url,location.href);let record={path:u.pathname,query:Object.fromEntries(u.searchParams),method:opts.method||'GET'};qa.requests.push(record);
if(qa.modalHold===u.pathname){await new Promise(resolve=>qa.releaseModal=resolve);if(qa.modalError)return new Response(JSON.stringify({detail:'Old modal error'}),{status:500});}
if(qa.listHold&&u.pathname==='/api/career-library'&&u.searchParams.get('q')===qa.listHold)await new Promise(resolve=>qa.releaseList=resolve);
return nativeFetch(input,opts);};
"""})
        async def check(name,expr):
            value=await b.evaluate(expr);ROWS.append({'id':name,'status':'PASS' if value is True else 'FAIL','actual':value})
            (OUT/'browser-latest.json').write_text(json.dumps(ROWS,ensure_ascii=False,indent=2),encoding='utf8')
        async def key(name,code):
            await b.call('Page.bringToFront')
            down={'type':'keyDown','key':name,'code':name,'windowsVirtualKeyCode':code}
            if name=='Enter':down['text']='\r'
            await b.call('Input.dispatchKeyEvent',down);await b.call('Input.dispatchKeyEvent',{'type':'keyUp','key':name,'code':name,'windowsVirtualKeyCode':code})
        for width in (1440,768,390,360):
            await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000 if width>=768 else 844,'deviceScaleFactor':1,'mobile':width<768})
            await b.call('Page.navigate',{'url':origin+'/'})
            await b.wait_for("document.querySelectorAll('[data-field]').length===12")
            await b.wait_for("document.fonts.status==='loaded'")
            await check(f'A.{width}.layout-nav-hero',"document.querySelectorAll('.journey-links a').length===4&&document.querySelectorAll('.journey-links a svg').length===4&&document.querySelector('.journey-nav').getBoundingClientRect().top>=document.querySelector('.hero').getBoundingClientRect().bottom-1&&document.documentElement.scrollWidth<=document.documentElement.clientWidth&&!document.body.innerText.includes('Góc hướng nghiệp')")
            await check(f'A.{width}.adjacent-CTA',"(()=>{let a=document.querySelector('.hero-actions a'),b=document.querySelector('#account-button'),r=a.getBoundingClientRect(),s=b.getBoundingClientRect();return a.pathname==='/ai-career-advisor'&&r.right<=s.left+1&&Math.abs(r.top-s.top)<3})()")
            await b.screenshot(f'qa/home-{width}.png')
            await b.evaluate("document.querySelector('.journey-links a[href=\"#careers\"]').click()")
            await asyncio.sleep(.7)
            await check(f'A.{width}.sticky-active-clearance',"document.querySelector('.journey-links a[href=\"#careers\"]').getAttribute('aria-current')==='location'&&document.querySelector('#careers').getBoundingClientRect().top>=document.querySelector('.journey-nav').getBoundingClientRect().bottom-2")
            await check(f'C.{width}.categories-first',"document.querySelectorAll('[data-field]').length===12&&document.querySelectorAll('.library-card').length===0")
            await b.evaluate("document.querySelector('#show-all').focus()")
            await key('Enter',13)
            await b.wait_for("document.querySelectorAll('.library-card').length===12")
            await b.evaluate("document.querySelector('#library-more').click()")
            await b.wait_for("document.querySelectorAll('.library-card').length===24")
            await check(f'C.{width}.pagination-count',"document.querySelector('#career-status').textContent.includes('200')&&document.querySelector('#career-status').textContent.includes('24')&&new Set([...document.querySelectorAll('.library-card h3')].map(x=>x.textContent)).size===24")
            await b.evaluate("document.querySelector('#career-search').value='bac si';document.querySelector('#search-form').requestSubmit()")
            await b.wait_for("document.querySelectorAll('.library-card').length>=1&&document.querySelector('.library-card h3').textContent==='Bác sĩ'")
            await b.evaluate("document.querySelector('.library-card').focus()")
            await key('Enter',13)
            await b.wait_for("!!document.querySelector('.library-modal-actions')")
            await check(f'C.{width}.modal-details-CTA',"document.querySelector('#content-dialog').open&&document.querySelector('#dialog-title').textContent==='Bác sĩ'&&document.querySelectorAll('#dialog-content li').length>=7&&document.querySelector('.library-modal-actions a').href.includes('career_id=bac-si')&&document.querySelectorAll('.library-modal-actions a')[1].href.includes('nghe=bac-si')")
            await b.screenshot(f'qa/modal-{width}.png');await key('Escape',27)
            await check(f'A.{width}.modal-Escape-focus',"!document.querySelector('#content-dialog').open&&document.activeElement.classList.contains('library-card')")
            if width==1440:
                # Deterministic response-order reproduction; real local catalog responses.
                await b.evaluate("qa.modalHold='/api/career-library/lap-trinh';void openLibraryCareer('lap-trinh')")
                await b.wait_for("!!qa.releaseModal")
                await b.evaluate("document.querySelector('#content-dialog').close();openLibraryCareer('bac-si')")
                await b.wait_for("document.querySelector('#dialog-title').textContent==='Bác sĩ'")
                await b.evaluate("qa.releaseModal();qa.modalHold=null")
                await asyncio.sleep(.3)
                await check('C.modal-latest-response-wins',"document.querySelector('#dialog-title').textContent==='Bác sĩ'&&document.querySelector('.library-modal-actions a').href.includes('career_id=bac-si')")
                await b.screenshot('qa/modal-response-order.png')
                await b.evaluate("document.querySelector('#content-dialog').close();qa.modalHold='/api/career-library/lap-trinh';qa.modalError=true;qa.releaseModal=null;void openLibraryCareer('lap-trinh')")
                await b.wait_for("!!qa.releaseModal&&document.querySelector('#dialog-title').textContent==='Đang mở nghề…'")
                await b.evaluate("document.querySelector('#content-dialog').close();openLibraryCareer('bac-si')")
                await b.wait_for("document.querySelector('#dialog-title').textContent==='Bác sĩ'")
                await b.evaluate("qa.releaseModal();qa.modalHold=null")
                await asyncio.sleep(.25)
                await check('C.modal-stale-error-cannot-overwrite',"document.querySelector('#dialog-title').textContent==='Bác sĩ'")
                await b.evaluate("qa.modalError=false;document.querySelector('#content-dialog').close();qa.listHold='lap trinh';document.querySelector('#career-search').value='lap trinh';document.querySelector('#search-form').requestSubmit()")
                await b.wait_for("!!qa.releaseList")
                await b.evaluate("document.querySelector('[data-field=health]').click()")
                await b.wait_for("document.querySelectorAll('.library-card').length===12")
                await b.evaluate("qa.releaseList();qa.listHold=null")
                await asyncio.sleep(.3)
                await check('C.list-query-category-race',"document.querySelector('[data-field=health]').getAttribute('aria-pressed')==='true'&&[...document.querySelectorAll('.library-tag')].every(x=>x.textContent==='Y tế và chăm sóc sức khỏe')")
            # Guest identity per viewport. No real Firebase provider is used.
            await b.evaluate("sessionStorage.clear()")
            for mode in ('career_discovery','career_exploration'):
                await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode='+mode+('&career_id=bac-si' if mode.endswith('exploration') else '')})
                await b.wait_for("!document.querySelector('#career-survey').hidden&&!document.querySelector('#survey-next').disabled")
                await check(f'B.{width}.{mode}.survey-ready',"!document.querySelector('#survey-answer').disabled&&document.querySelector('#survey-step').textContent.includes('1 / 5')&&document.querySelector('#guest-banner').hidden===false")
                await b.evaluate("document.querySelector('#survey-suggestions button').click()")
                await check(f'B.{width}.{mode}.chip-free-edit',"document.querySelector('#survey-answer').value.length>0")
                await b.evaluate("document.querySelector('#survey-address').value='anh';document.querySelector('#survey-address').dispatchEvent(new Event('change'));document.querySelector('#survey-answer').value='Em thích vẽ và máy tính';document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click();document.querySelector('#survey-back').click()")
                await check(f'B.{width}.{mode}.back-edit-address',"document.querySelector('#survey-answer').value==='Em thích vẽ và máy tính'&&document.querySelector('#survey-address').value==='anh'")
                for step in range(5):await b.evaluate("document.querySelector('#survey-answer').value='Vẽ, tìm hiểu máy tính và làm việc kiên nhẫn';document.querySelector('#survey-next').click()")
                if mode.endswith('exploration'):
                    await b.wait_for("document.querySelector('#career-survey').hidden&&document.querySelector('#message-input').value.includes('Bác sĩ')&&!document.querySelector('#send-message').disabled")
                    await check(f'B.{width}.exploration-no-autosend',"document.querySelectorAll('.message-row').length===1&&qa.requests.filter(r=>r.path==='/api/ai/chat').length===0")
                    await b.evaluate("document.querySelector('#message-input').value+=' Em muốn biết cách học.';document.querySelector('#message-input').dispatchEvent(new Event('input'))")
                    await b.screenshot(f'qa/exploration-draft-{width}.png')
                    await b.evaluate("document.querySelector('#send-message').click()")
                await b.wait_for("document.querySelectorAll('.message-row').length===3&&!document.querySelector('#message-input').disabled")
                await check(f'B.{width}.{mode}.chat-survey-hidden',"document.querySelector('#career-survey').hidden&&document.documentElement.scrollWidth<=document.documentElement.clientWidth")
                await b.call('Page.reload')
                await b.wait_for("document.querySelectorAll('.message-row').length===3")
                await check(f'B.{width}.{mode}.reload-context',"document.querySelector('#career-survey').hidden"+("&&document.querySelector('#session-note').textContent.includes('Bác sĩ')" if mode.endswith('exploration') else ''))
                await b.screenshot(f'qa/{mode}-{width}.png')
            await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=bac-si'})
            await b.wait_for("!document.querySelector('#story-content').hidden")
            await check(f'D.{width}.direct-story-first-scene',"document.querySelector('#career-title').textContent.includes('bác sĩ')&&document.querySelector('#scene-counter').textContent.includes('1 / 4')")
            await b.evaluate("document.querySelector('[data-career-id=lap-trinh]').click()")
            await b.wait_for("document.querySelector('#career-title').textContent.includes('lập trình')")
            await b.evaluate('history.back()')
            await b.wait_for("document.querySelector('#career-title').textContent.includes('bác sĩ')&&!document.querySelector('#story-content').hidden")
            await b.evaluate('history.forward()')
            await b.wait_for("document.querySelector('#career-title').textContent.includes('lập trình')")
            await check(f'D.{width}.back-forward-correct-career',"document.querySelector('#scene-counter').textContent.includes('1 / 4')&&location.search.includes('lap-trinh')")
            await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=ky-su-du-lieu'})
            await b.wait_for("!document.querySelector('#story-error').hidden")
            await check(f'D.{width}.missing-story-no-fallback',"document.querySelector('#story-error').textContent.includes('đang được cập nhật')&&document.querySelector('#story-content').hidden&&location.search.includes('ky-su-du-lieu')")
        await b.evaluate("sessionStorage.setItem('__fixture_login','1')")
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_exploration&career_id=lap-trinh'})
        await b.wait_for("!document.querySelector('#career-survey').hidden&&!document.querySelector('#survey-next').disabled")
        for step in range(5):await b.evaluate("document.querySelector('#survey-answer').value='Muốn tìm hiểu máy tính và làm việc sáng tạo';document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelector('#message-input').value.includes('Lập trình viên')&&!document.querySelector('#send-message').disabled")
        await check('E.member-exploration-editable-no-autosend',"document.querySelectorAll('.message-row').length===1&&document.querySelector('#guest-banner').hidden")
        await b.evaluate("document.querySelector('#send-message').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===3")
        await b.call('Page.reload')
        await b.wait_for("document.querySelectorAll('.message-row').length===3")
        await check('E.member-history-mode-survey-reload',"document.querySelector('#career-survey').hidden&&document.querySelector('#session-note').textContent.includes('Lập trình viên')")
        await b.evaluate("document.querySelector('#logout').click()")
        await b.wait_for("location.pathname==='/'")
        await check('E.member-logout',"!sessionStorage.getItem('__fixture_login')")
        await check('F.browser-runtime-exceptions',json.dumps(not b.errors))
        await check('F.browser-console-errors',json.dumps(not CONSOLE_ERRORS))
        unexpected=[r for r in REQUEST_ERRORS if not (r.get('status')==404 and '/api/career-stories/ky-su-du-lieu' in r.get('url',''))]
        await check('F.browser-unexpected-resource-errors',json.dumps(not unexpected))
        (OUT/'browser-network-console.json').write_text(json.dumps({'console':CONSOLE_ERRORS,'requests':REQUEST_ERRORS,'unexpected':unexpected},ensure_ascii=False,indent=2),encoding='utf8')
        (OUT/'browser-errors.json').write_text(json.dumps(b.errors,ensure_ascii=False,indent=2),encoding='utf8')
        print(json.dumps({'summary':{s:sum(r['status']==s for r in ROWS) for s in ('PASS','FAIL')},'failed':[r for r in ROWS if r['status']=='FAIL']},ensure_ascii=True))

if __name__=='__main__':
    OUT.mkdir(exist_ok=True,parents=True)
    with LocalPostgres() as pg:
        with psycopg.connect(pg.url,autocommit=True) as db:
            for name in ('001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql'):db.execute((h.ROOT/'migrations'/name).read_text(encoding='utf8'))
        os.environ['LABAN_BROWSER_TEST_DATABASE']=pg.url
        h.checks=checks;h.main()
