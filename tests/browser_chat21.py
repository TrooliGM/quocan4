"""Actual Chrome + local PostgreSQL; Firebase fixture and AI demo, never live provider."""
import json
import os
import sys
from pathlib import Path
import websockets
import psycopg
import browser_smoke as h
from postgres_fixture import LocalPostgres

RESULTS=[]
def record(name):
    RESULTS.append({'name':name,'status':'PASS'})
    print('PASS '+name,flush=True)
    report='chat21-mobile-results.json' if '--draft-only' in sys.argv else 'chat21-browser-results.json'
    (h.ARTIFACTS/report).write_text(json.dumps({'checks':RESULTS,'firebase':'fixture','ai':'demo','database':'isolated loopback'},indent=2),encoding='utf8')

async def checks(url,origin):
    async with websockets.connect(url,origin='http://localhost:9227',max_size=20000000) as ws:
        b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
        await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_exploration&career_id=chuyen-vien-nhan-su'})
        await b.wait_for("!document.querySelector('#career-survey').hidden && !document.querySelector('#survey-next').disabled")
        sid=await b.evaluate("Object.keys(sessionStorage).find(k=>k.startsWith('laban.advisor.')) && sessionStorage.getItem(Object.keys(sessionStorage).find(k=>k.startsWith('laban.advisor.')))")
        assert await b.evaluate("document.querySelector('#survey-answer').value==='' && document.querySelectorAll('#survey-suggestions button').length===6")
        await b.evaluate("document.querySelector('#survey-suggestions button').click()")
        first=await b.evaluate("document.querySelector('#survey-answer').value")
        assert len(first)>30
        assert await b.evaluate("document.querySelector('#survey-step').textContent.includes('1 / 5')")
        await b.evaluate("document.querySelector('#survey-answer').value+=' Em muốn thêm ý riêng.';document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
        await b.evaluate("document.querySelector('#survey-answer').value='Em thích làm việc nhóm';document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
        await b.evaluate("document.querySelector('#survey-answer').value='Em chưa rõ điểm mạnh';document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-address').value='anh';document.querySelector('#survey-address').dispatchEvent(new Event('change'))")
        await b.evaluate("document.querySelector('#survey-back').click()")
        assert await b.evaluate("document.querySelector('#survey-answer').value==='Em thích làm việc nhóm'")
        await b.evaluate("document.querySelector('#survey-next').click()")
        assert await b.evaluate("document.querySelector('#survey-answer').value==='Em chưa rõ điểm mạnh'")
        record('Rich suggestions append without submit; editing/back preserves answers')
        await b.call('Page.reload')
        await b.wait_for("document.querySelector('#survey-step')?.textContent.includes('3 / 5') && !document.querySelector('#survey-next').disabled")
        assert await b.evaluate("document.querySelector('#survey-answer').value==='Em chưa rõ điểm mạnh' && document.querySelector('#survey-address').value==='anh'")
        record('Reload restores survey step, answer and address')
        await b.evaluate("document.querySelector('#guest-login').click()")
        await b.wait_for("location.pathname==='/' && document.querySelector('#auth-dialog')?.open && !document.querySelector('#auth-submit').disabled")
        # Inject one network-style claim failure; actual retry still uses backend ownership checks.
        await b.evaluate("window.savedFetch=window.fetch;window.fetch=(path,options)=>path==='/api/ai/guest/claim'?Promise.resolve(new Response('{}',{status:503})):window.savedFetch(path,options)")
        await b.evaluate("document.querySelector('#auth-email').value='fixture@example.com';document.querySelector('#auth-password').value='fixture-password';document.querySelector('#auth-form').requestSubmit()")
        await b.wait_for("!document.querySelector('#guest-claim-retry').hidden && !document.querySelector('#auth-submit').disabled")
        assert await b.evaluate("location.pathname==='/' && !!sessionStorage.getItem('laban.claim-target')")
        # Reload rehydrates the pending server-cookie claim and returns to same conversation.
        await b.call('Page.reload')
        await b.wait_for("location.pathname==='/ai-career-advisor' && document.querySelector('#survey-step')?.textContent.includes('3 / 5') && !document.querySelector('#survey-next').disabled")
        assert await b.evaluate("document.querySelector('#survey-answer').value==='Em chưa rõ điểm mạnh' && document.querySelector('#survey-address').value==='anh'")
        assert await b.evaluate(f"sessionStorage.getItem('laban.advisor.browser-user')==={json.dumps(sid)}")
        record('Guest -> email fixture preserves same conversation and survey after failed claim + reload')
        for answer in ['Em chưa rõ điểm mạnh','Em muốn giúp người khác','Em muốn hiểu khó khăn của nghề']:
            await b.evaluate(f"document.querySelector('#survey-answer').value={json.dumps(answer)};document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelector('#career-survey').hidden && document.querySelector('#message-input').value.includes('Chuyên viên nhân sự') && !document.querySelector('#send-message').disabled")
        assert await b.evaluate("document.querySelectorAll('.message-row').length===1 && document.querySelector('#message-input').value.includes('thử thách')")
        await b.evaluate("document.querySelector('#message-input').value+=' Em muốn hỏi thêm về đào tạo.';document.querySelector('#message-input').dispatchEvent(new Event('input'))")
        await b.call('Page.reload')
        await b.wait_for("document.querySelector('#message-input').value.includes('đào tạo.') && !document.querySelector('#send-message').disabled")
        record('Career-specific question waits for Send and retains edits across reload')
        await b.screenshot('chat21-desktop-draft.png')
        await b.evaluate("document.querySelector('#send-message').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===3 && !document.querySelector('#message-input').disabled")
        await b.evaluate("document.querySelector('.history-item .icon-button').click()")
        await b.wait_for("document.querySelector('#action-dialog').open")
        await b.evaluate("document.querySelector('#rename-input').value='Tên em tự chọn';document.querySelector('#action-form').requestSubmit()")
        await b.wait_for("document.querySelector('.history-open strong')?.textContent==='Tên em tự chọn'")
        await b.evaluate("document.querySelector('#message-input').value='Em muốn biết thêm';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#send-message').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===5 && !document.querySelector('#message-input').disabled")
        assert await b.evaluate("document.querySelector('.history-open strong').textContent==='Tên em tự chọn'")
        record('Manually renamed title survives subsequent chat')
        for cid,name in [('lap-trinh','Lập trình viên'),('bac-si','Bác sĩ'),('giao-vien','Giáo viên')]:
            await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_exploration&career_id='+cid})
            await b.wait_for("document.querySelector('#career-survey')?.hidden===false && !document.querySelector('#survey-next').disabled")
            for _ in range(5):await b.evaluate("document.querySelector('#survey-answer').value='Em muốn khám phá thêm';document.querySelector('#survey-next').click()")
            await b.wait_for(f"document.querySelector('#message-input').value.includes({json.dumps(name)}) && !document.querySelector('#send-message').disabled")
            assert await b.evaluate("!document.querySelector('#message-input').value.includes('Chuyên viên nhân sự') && document.querySelectorAll('.message-row').length===1")
        record('Changing career resets draft to correct programmer/doctor/teacher context')
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_discovery'})
        await b.wait_for("document.querySelector('#career-survey')?.hidden===false && !document.querySelector('#survey-next').disabled")
        for _ in range(5):await b.evaluate("document.querySelector('#survey-answer').value='Em chưa rõ sở thích';document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===3 && !document.querySelector('#message-input').disabled")
        assert await b.evaluate("document.querySelector('.history-open strong').textContent==='Khám phá nghề phù hợp' && !document.querySelector('#messages').textContent.includes('Hãy phân tích khảo sát')")
        record('Discovery title and visible message exclude internal analysis command')
        # Homepage-origin Google fixture stays home, while login cancellation keeps drafts.
        await b.call('Page.navigate',{'url':origin+'/'})
        await b.evaluate("sessionStorage.removeItem('__fixture_login')")
        await b.call('Page.reload')
        await b.wait_for("!document.querySelector('#auth-submit').disabled")
        await b.evaluate("document.querySelector('[data-open-auth]').click();document.querySelector('#google-signin').click()")
        await b.wait_for("location.pathname==='/' && !sessionStorage.getItem('laban.login-return') && document.querySelector('#account-label').textContent==='Tài khoản'")
        record('Homepage Google fixture login returns to homepage')
        for method in ('popup','redirect'):
            await b.evaluate("sessionStorage.removeItem('__fixture_login')")
            await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_exploration&career_id=bac-si'})
            await b.wait_for("document.querySelector('#career-survey')?.hidden===false && !document.querySelector('#survey-next').disabled")
            await b.evaluate("document.querySelector('#survey-answer').value='Nội dung chờ đăng nhập Google';document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#guest-login').click()")
            await b.wait_for("location.pathname==='/' && document.querySelector('#auth-dialog')?.open && !document.querySelector('#google-signin').disabled")
            # Reproduce the old fallback-to-home path: loss of only the return-intent record.
            await b.evaluate("sessionStorage.removeItem('laban.login-return')")
            if method=='popup':
                await b.evaluate("sessionStorage.setItem('__fixture_cancel_google','1');document.querySelector('#google-signin').click()")
                await b.wait_for("document.querySelector('#auth-status').textContent.includes('đóng') && !document.querySelector('#google-signin').disabled")
                assert await b.evaluate("new URLSearchParams(location.search).get('return_to').includes('/ai-career-advisor')")
                await b.evaluate("sessionStorage.removeItem('__fixture_cancel_google');document.querySelector('#google-signin').click()")
            else:
                await b.evaluate("sessionStorage.setItem('__fixture_login','1');sessionStorage.setItem('__fixture_redirect','1')")
                await b.call('Page.reload')
            await b.wait_for("location.pathname==='/ai-career-advisor' && document.querySelector('#survey-answer')?.value==='Nội dung chờ đăng nhập Google' && !document.querySelector('#survey-next').disabled")
            record('Google '+method+' fixture preserves guest survey, including cancellation/reload')
        for width in (1440,390):
            await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000,'deviceScaleFactor':1,'mobile':width<600})
            await b.call('Page.navigate',{'url':origin+'/'})
            await b.wait_for("document.querySelectorAll('[data-field]').length===12")
            await b.evaluate("window.openLibraryCareer('kiem-sat-vien')")
            await b.wait_for("document.querySelectorAll('.career-profile-section').length===5")
            assert await b.evaluate("document.querySelector('#dialog-content').textContent.includes('gỡ tội') && document.querySelector('.library-modal-actions a').href.includes('career_id=kiem-sat-vien')")
            assert await b.evaluate("document.querySelectorAll('.library-modal-actions a').length===2 && document.documentElement.scrollWidth<=innerWidth+1")
            await b.screenshot(f'chat21-profile-{width}.png')
        record('Deep prosecutor profile, disclosure and two links desktop/mobile without overflow')
        assert not b.errors,b.errors
        record('No uncaught browser exceptions')

async def draft_checks(url,origin):
    async with websockets.connect(url,origin='http://localhost:9227',max_size=20000000) as ws:
        b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
        await b.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_exploration&career_id=chuyen-vien-nhan-su'})
        await b.wait_for("!document.querySelector('#career-survey').hidden && !document.querySelector('#survey-next').disabled")
        assert await b.evaluate("document.documentElement.scrollWidth<=innerWidth+1 && document.querySelector('#survey-answer').value===''")
        await b.screenshot('chat21-mobile-survey.png')
        for i in range(5):
            assert await b.evaluate("[...document.querySelectorAll('#survey-suggestions button')].every(b=>b.textContent.length>30)")
            await b.evaluate("document.querySelector('#survey-suggestions button').click();document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelector('#career-survey').hidden && !document.querySelector('#send-message').disabled")
        assert await b.evaluate("document.querySelector('#message-input').value.includes('Quản lý hồ sơ') && document.querySelectorAll('.message-row').length===1 && document.documentElement.scrollWidth<=innerWidth+1")
        await b.screenshot('chat21-mobile-career-draft.png')
        record('Mobile rich survey and grounded HR draft: no overflow, no automatic send')
        await b.evaluate("document.querySelector('#message-input').value='';document.querySelector('#message-input').dispatchEvent(new Event('input'))")
        await b.call('Page.reload')
        await b.wait_for("!document.querySelector('#chat-app').hidden && document.querySelector('#career-survey').hidden && document.querySelector('#session-note').textContent.includes('nhân sự')")
        assert await b.evaluate("document.querySelector('#message-input').value==='' && document.querySelectorAll('.message-row').length===1")
        record('Explicitly cleared career question remains blank after reload')
        assert not b.errors,b.errors

if __name__=='__main__':
    # Drop all inherited provider credentials. No dotenv exists in this fresh worktree.
    safe={k:v for k,v in os.environ.items() if not k.startswith(('DEEPSEEK','FIREBASE','VBEE','GOOGLE','DATABASE','AI_'))}
    os.environ.clear();os.environ.update(safe)
    os.environ['LABAN_TEST_PG_BIN']='D:/khkt/artifacts/postgres-tools/pgsql/bin'
    os.environ.update(AI_USER_PER_MINUTE='100',AI_IP_PER_MINUTE='200',AI_USER_PER_DAY='200',AI_IP_PER_DAY='300',AI_GUEST_CREATE_PER_DAY='20',AI_GUEST_CREATE_PER_MINUTE='10')
    with LocalPostgres() as pg:
        with psycopg.connect(pg.url,autocommit=True) as db:
            for migration in ('001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql'):
                db.execute((h.ROOT/'migrations'/migration).read_text(encoding='utf8'))
        os.environ['LABAN_BROWSER_TEST_DATABASE']=pg.url
        h.checks=draft_checks if '--draft-only' in sys.argv else checks;h.main()
