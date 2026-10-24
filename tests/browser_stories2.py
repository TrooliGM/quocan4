"""Chrome thật + PostgreSQL local riêng; Firebase fixture, AI demo có nhãn."""
import asyncio
import json
import os
import sys
import websockets
import psycopg
import browser_smoke as h
from postgres_fixture import LocalPostgres

CHECKS=[]
def passed(name):
    CHECKS.append(name);print('PASS '+name,flush=True)
    (h.ARTIFACTS/'stories2-browser.json').write_text(json.dumps({'checks':CHECKS,'firebase':'fixture','ai':'demo','database':'local isolated'},ensure_ascii=False,indent=2),encoding='utf8')

async def checks(url,origin):
    async with websockets.connect(url,origin='http://localhost:9227',max_size=20000000) as ws:
        b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
        await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
        await b.call('Page.addScriptToEvaluateOnNewDocument',{'source':"""
window.storyNetwork=[];const realFetch=window.fetch;
window.fetch=async(url,options={})=>{storyNetwork.push({url:String(url),method:options.method||'GET',body:options.body||''});return realFetch(url,options);};
"""})
        await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=kiem-sat-vien'})
        await b.wait_for("document.querySelector('#story-content')?.hidden===false")
        assert await b.evaluate("document.querySelector('#career-title').textContent.includes('gỡ tội') && document.querySelector('#scene-counter').textContent==='Cảnh 1 / 5'")
        assert await b.evaluate("storyNetwork.filter(r=>r.url.startsWith('/api/')).length===2 && storyNetwork.every(r=>r.method==='GET')")
        passed('Exact library ID deep link, two read-only API requests, no authentication/AI to read')
        await b.evaluate("document.querySelector('#next-scene').click();document.querySelector('[data-choice=option-1]').click()")
        feedback=await b.evaluate("document.querySelector('#decision-feedback').textContent")
        assert 'toàn diện' in feedback
        await asyncio.sleep(.2)
        assert await b.evaluate("document.querySelector('#scene-counter').textContent==='Cảnh 2 / 5'")
        await b.evaluate("document.querySelector('[data-choice=option-2]').click()")
        assert await b.evaluate("document.querySelector('#decision-feedback').textContent")!=feedback
        await b.evaluate("document.querySelector('#next-scene').click()")
        assert await b.evaluate("!document.querySelector('#scene-consequence').hidden && document.querySelector('#scene-consequence').textContent.includes('Người phụ trách')")
        await b.evaluate("document.querySelector('#prev-scene').click()")
        assert await b.evaluate("document.querySelector('[data-choice=option-2]').getAttribute('aria-pressed')==='true'")
        passed('Choices can change; distinct feedback and next-scene consequence; previous restores choice; no autoplay')
        await b.evaluate("document.querySelector('#finish-story').click()")
        assert await b.evaluate("document.querySelectorAll('#summary-decisions li').length===2 && document.querySelector('#summary-decisions').textContent.includes('chưa chọn')")
        await b.evaluate("document.querySelector('#restart-story').click();document.querySelector('#next-scene').click()")
        assert await b.evaluate("document.querySelector('#decision-feedback').hidden && document.querySelector('#day-summary').hidden")
        passed('Summary includes decisions; replay clears choices')
        await b.evaluate("document.querySelector('#story-search').value='dieu duong';document.querySelector('#story-search').dispatchEvent(new Event('input'))")
        assert await b.evaluate("document.querySelector('[data-career-id=dieu-duong]')!==null")
        await b.evaluate("document.querySelector('#story-search').value='kiem sat';document.querySelector('#story-search').dispatchEvent(new Event('input'))")
        assert await b.evaluate("document.querySelectorAll('[data-career-id]').length===1")
        await b.evaluate("document.querySelector('[data-career-id]').click()")
        await b.wait_for("!document.querySelector('#story-content').hidden && document.querySelector('#scene-counter').textContent==='Cảnh 1 / 5'")
        await b.evaluate("document.querySelector('#next-scene').click();document.querySelector('[data-choice=option-1]').click();document.querySelector('#player').scrollIntoView()")
        await b.screenshot('stories2-desktop.png')
        await b.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
        assert await b.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
        await b.screenshot('stories2-mobile.png')
        await b.evaluate("document.querySelector('#mode-comic').click()")
        assert await b.evaluate("document.querySelectorAll('.comic-panel').length===5 && document.querySelector('#player').hidden")
        await b.evaluate("document.querySelector('[data-open-scene=\"3\"]').click()")
        assert await b.evaluate("document.querySelector('#scene-counter').textContent==='Cảnh 4 / 5' && !document.querySelector('#player').hidden")
        passed('Search without accents, explicit reopen starts at scene 1, desktop/mobile and comic navigation')
        # Deliberately retain a response after abort to exercise stale-response guard.
        await b.evaluate("window.savedFetch=fetch;fetch=async(...a)=>{const r=await savedFetch(...a);if(String(a[0]).endsWith('/lap-trinh'))await new Promise(x=>setTimeout(x,300));return r;};history.pushState({},'', '?nghe=lap-trinh');dispatchEvent(new PopStateEvent('popstate'));setTimeout(()=>{history.pushState({},'', '?nghe=kiem-sat-vien&scene=scene-4');dispatchEvent(new PopStateEvent('popstate'));},40)")
        await b.wait_for("!document.querySelector('#story-content').hidden && document.querySelector('#career-title').textContent.includes('gỡ tội')")
        await asyncio.sleep(.5)
        assert await b.evaluate("document.querySelector('#career-title').textContent.includes('gỡ tội') && document.querySelector('#scene-counter').textContent==='Cảnh 4 / 5'")
        passed('Rapid story switching ignores stale response and does not duplicate popstate handler')
        await b.evaluate("document.querySelector('#story-question').value='Vì sao cần đúng thẩm quyền trong tình huống này?';document.querySelector('#story-ask-form').requestSubmit()")
        await b.wait_for("document.querySelector('#career-survey')?.hidden===false && !document.querySelector('#survey-next').disabled",timeout=45)
        for _ in range(5):
            await b.evaluate("document.querySelector('#survey-suggestions button').click();document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelector('#career-survey').hidden && document.querySelector('#message-input').value.includes('scene-4')",timeout=45)
        assert await b.evaluate("document.querySelector('#message-input').value.includes('Vì sao cần đúng thẩm quyền') && document.querySelector('#message-input').value.includes('gỡ tội') && storyNetwork.every(r=>r.url!='/api/ai/chat')")
        assert await b.evaluate("document.querySelector('#session-note a')?.href.includes('scene=scene-4')")
        passed('Guest exploration retains editable exact scene/title/context after five-step survey, no automatic DeepSeek')
        await b.evaluate("document.querySelector('#send-message').click()")
        await b.wait_for("document.querySelectorAll('.message-row.user').length===1 && document.querySelectorAll('.message-row.assistant').length===2",timeout=45)
        assert await b.evaluate("storyNetwork.filter(r=>r.url==='/api/ai/chat').length===1 && JSON.parse(storyNetwork.find(r=>r.url==='/api/ai/chat').body).message.includes('scene-4')")
        passed('Only explicit send invokes protected chat once, with story context (local demo)')
        await b.evaluate("document.querySelector('#session-note a').click()")
        await b.wait_for("document.querySelector('#story-content')?.hidden===false")
        assert await b.evaluate("document.querySelector('#scene-counter').textContent==='Cảnh 4 / 5'")
        await b.evaluate("document.querySelector('#prev-scene').click();document.querySelector('#prev-scene').click()")
        assert await b.evaluate("document.querySelector('[data-choice=option-1]').getAttribute('aria-pressed')==='true'")
        passed('Return from AI restores scene and earlier choice without database choice storage')
        await b.evaluate("document.querySelector('#back-career').click()")
        await b.wait_for("document.querySelector('#content-dialog')?.open && document.querySelector('#dialog-title').textContent==='Kiểm sát viên'")
        assert await b.evaluate("document.querySelector('.library-modal-actions a:last-child').href.includes('nghe=kiem-sat-vien')")
        passed('Back opens exact approved career profile, both existing action buttons preserved')
        await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=not-a-career'})
        await b.wait_for("document.querySelector('#story-error')?.hidden===false")
        assert await b.evaluate("document.querySelector('#story-content').hidden")
        assert not b.errors,b.errors
        passed('Unknown ID shows controlled error; no uncaught JavaScript exceptions')

if __name__=='__main__':
    safe={k:v for k,v in os.environ.items() if not k.startswith(('DEEPSEEK','FIREBASE','VBEE','GOOGLE','DATABASE','AI_'))}
    os.environ.clear();os.environ.update(safe)
    os.environ['LABAN_TEST_PG_BIN']='D:/khkt/artifacts/postgres-tools/pgsql/bin'
    with LocalPostgres() as pg:
        with psycopg.connect(pg.url,autocommit=True) as db:
            for migration in ('001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql'):
                db.execute((h.ROOT/'migrations'/migration).read_text(encoding='utf8'))
        os.environ['LABAN_BROWSER_TEST_DATABASE']=pg.url
        h.checks=checks;h.main()
