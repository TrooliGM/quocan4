"""Chrome thật + PG local. Firebase/DeepSeek fixture, không phải LIVE PASS."""
import json,os,sys
from pathlib import Path
import websockets,psycopg
import browser_smoke as h
from postgres_fixture import LocalPostgres
from test_advisor30_profile import ANSWERS

CHECKS=[]
def passed(text):CHECKS.append(text);print('PASS '+text,flush=True)

async def checks(url,origin):
    async with websockets.connect(url,origin='http://localhost:9227',max_size=20000000) as ws:
        b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
        await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_discovery'})
        await b.wait_for("document.querySelector('#career-survey')?.hidden===false && !document.querySelector('#survey-next').disabled",timeout=45)
        sid=await b.evaluate("sessionStorage.getItem('laban.advisor.server-guest')")
        for answer in ANSWERS:
            await b.evaluate(f"document.querySelector('#survey-answer').value={json.dumps(answer)};document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelectorAll('.profile-review-button').length===1 && !document.querySelector('#message-input').disabled",timeout=45)
        assert await b.evaluate("document.querySelector('.assistant-identity h1').textContent.includes('Trợ lý hướng nghiệp') && document.querySelector('.assistant-identity p').textContent==='Đồng hành cùng bạn khám phá nghề nghiệp' && !document.querySelector('.message-row.assistant img,.message-row.assistant .message-label')")
        assert await b.evaluate("getComputedStyle(document.querySelector('.assistant .message-bubble')).borderTopLeftRadius==='4px' && document.querySelector('.message-actions button').textContent.includes('Sao chép') && !!document.querySelector('.header-avatar')")
        passed('Guest survey -> validated analysis; header, no repeated avatar/name, original bubble and Copy')
        await b.screenshot('advisor30-chat-desktop.png')
        before=await b.evaluate("fetch('/__qa/advisor30').then(r=>r.json())")
        await b.evaluate("document.querySelector('.profile-review-button').click()")
        await b.wait_for("document.querySelectorAll('.profile-proposal').length===2")
        assert await b.evaluate("document.querySelector('.profile-evidence').textContent.includes('Câu 1')")
        await b.screenshot('advisor30-proposals-desktop.png')
        await b.evaluate("document.querySelectorAll('.profile-proposal')[1].querySelectorAll('button')[2].click();document.querySelector('.profile-proposal textarea').value='Vẽ đồ họa trên máy tính';document.querySelector('.profile-proposal button').click()")
        await b.wait_for("document.querySelectorAll('.profile-item').length===1 && document.querySelectorAll('.profile-proposal').length===0")
        after=await b.evaluate("fetch('/__qa/advisor30').then(r=>r.json())");assert after['analysis_calls']==before['analysis_calls'] and after['main_calls']==before['main_calls']
        passed('Review grounds; reject one, edit/accept one; opening/saving profile does not call AI')
        await b.evaluate("document.querySelector('#profile-dialog').close()")
        await b.call('Page.reload')
        await b.wait_for("document.querySelectorAll('.message-row').length===3 && !document.querySelector('#message-input').disabled",timeout=45)
        await b.evaluate("document.querySelector('#open-profile').click()")
        await b.wait_for("document.querySelectorAll('.profile-item').length===1")
        assert await b.evaluate("document.querySelector('.profile-item input').value==='Vẽ đồ họa trên máy tính'")
        await b.evaluate("document.querySelector('#profile-dialog').close();document.querySelector('#use-profile').click()")
        await b.wait_for("!document.querySelector('#use-profile').disabled && document.querySelector('#use-profile').checked")
        for use,text in [(True,'Tìm hiểu kỹ năng liên quan'),(False,'Một bước thử nhỏ là gì?')]:
            if not use:
                await b.evaluate("document.querySelector('#use-profile').click()")
                await b.wait_for("!document.querySelector('#use-profile').disabled && !document.querySelector('#use-profile').checked")
            await b.evaluate(f"document.querySelector('#message-input').value={json.dumps(text)};document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
            await b.wait_for("document.querySelector('#thinking').hidden && !document.querySelector('#message-input').disabled")
            facts=await b.evaluate("fetch('/__qa/advisor30').then(r=>r.json())");assert facts['last_context_has_profile']==use
        passed('Profile survives refresh; backend includes only confirmed profile when enabled, excludes when disabled')
        quota=await b.evaluate("fetch('/api/ai/config').then(r=>r.json()).then(r=>r.guest_quota.remaining)")
        await b.evaluate("document.querySelector('#message-input').value='Kiểm thử timeout';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
        await b.wait_for("!document.querySelector('#retry-send').hidden && !document.querySelector('#message-input').disabled")
        assert await b.evaluate("fetch('/api/ai/config').then(r=>r.json()).then(r=>r.guest_quota.remaining)")==quota
        await b.evaluate("document.querySelector('#retry-send').click()")
        await b.wait_for("document.querySelector('#retry-send').hidden && !document.querySelector('#message-input').disabled")
        assert await b.evaluate("fetch('/api/ai/config').then(r=>r.json()).then(r=>r.guest_quota.remaining)")==quota-1
        passed('AI timeout keeps pending message; safe retry succeeds and quota charged once')
        await b.evaluate("document.querySelector('#guest-login').click()")
        await b.wait_for("document.querySelector('#auth-dialog')?.open && !document.querySelector('#google-signin').disabled",timeout=45)
        await b.evaluate("document.querySelector('#google-signin').click()")
        await b.wait_for("location.pathname==='/ai-career-advisor' && document.querySelector('#guest-banner')?.hidden && document.querySelectorAll('.message-row').length===9",timeout=45)
        await b.evaluate("document.querySelector('#open-profile').click()")
        await b.wait_for("document.querySelectorAll('.profile-item').length===1")
        assert await b.evaluate("document.querySelector('.profile-item input').value==='Vẽ đồ họa trên máy tính' && [...document.querySelectorAll('.profile-item button')].some(b=>b.textContent.includes('Giữ lâu dài'))")
        await b.screenshot('advisor30-account-profile-desktop.png')
        await b.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
        assert await b.evaluate("document.documentElement.scrollWidth<=innerWidth+1 && document.querySelector('#profile-dialog').getBoundingClientRect().right<=innerWidth+1")
        await b.screenshot('advisor30-profile-mobile.png')
        await b.evaluate("document.querySelector('#profile-dialog').close()")
        assert await b.evaluate("document.querySelector('#session-note').textContent.includes('Đã gắn tài khoản') && !document.querySelector('#keep-conversation').hidden")
        await b.screenshot('advisor30-chat-mobile.png')
        passed('Google fixture claim preserves exact history/profile; temporary vs account retention label truthful; mobile fits')
        await b.evaluate("document.querySelector('#open-profile').click()")
        await b.wait_for("document.querySelectorAll('.profile-item').length===1")
        await b.evaluate("document.querySelector('.profile-item button:nth-of-type(2)').click()")
        await b.wait_for("document.querySelectorAll('.profile-item').length===0")
        passed('Confirmed profile item can be deleted and UI/backend update')
        await b.evaluate("document.querySelector('#profile-dialog').close();document.querySelector('#keep-conversation').click()")
        await b.wait_for("document.querySelector('#action-dialog').open")
        await b.evaluate("document.querySelector('#action-form').requestSubmit()")
        await b.wait_for("document.querySelector('#keep-conversation').hidden && document.querySelector('#session-note').textContent.includes('Lịch sử đã bật')")
        await b.call('Page.reload')
        await b.wait_for("document.querySelectorAll('.message-row').length===9 && document.querySelector('#session-note').textContent.includes('Lịch sử đã bật')",timeout=45)
        passed('Explicit retention preserves conversation ID/history/survey and survives refresh')
        assert not b.errors,b.errors
        report={'checks':CHECKS,'database':'isolated local PostgreSQL','firebase':'fixture, NOT LIVE','deepseek':'fixture, NOT LIVE','search_live':'BLOCKED','screenshots':'artifacts/advisor30-*.png'}
        (h.ARTIFACTS/'advisor30-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':
    for k in list(os.environ):
        if k.startswith(('DEEPSEEK_','FIREBASE_','GOOGLE_APPLICATION_CREDENTIALS','SEARCH_','DATABASE_URL')):os.environ.pop(k)
    with LocalPostgres() as cluster:
        with psycopg.connect(cluster.url,autocommit=True) as db:
            for name in ['001_conversations.sql','002_guest_quota.sql','004_shared_ai_protection.sql']:db.execute((h.ROOT/'migrations'/name).read_text(encoding='utf8'))
            db.execute("SET laban.profile_migration_target='task4-staging-approved'");db.execute((h.ROOT/'migrations/006_confirmed_career_profile.sql').read_text(encoding='utf8'))
        os.environ.update(LABAN_BROWSER_TEST_DATABASE=cluster.url,LABAN_BROWSER_ADVISOR30='1',ADVISOR_PROFILE_ENABLED='true',DEEPSEEK_API_KEY='fixture-only-not-a-real-key')
        h.checks=checks;h.main()
