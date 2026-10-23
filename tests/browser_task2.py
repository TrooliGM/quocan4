"""Isolated PostgreSQL + Firebase stub + AI demo. No Neon/provider writes."""
import os
import json
import websockets
import psycopg
import browser_smoke as h
from postgres_fixture import LocalPostgres


async def checks(url,origin):
    async with websockets.connect(url,origin='http://localhost:9227',max_size=20000000) as ws:
        b=h.Browser(ws);await b.call('Runtime.enable');await b.call('Page.enable')
        for width in (1440,390):
            await b.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':1000,'deviceScaleFactor':1,'mobile':width<600})
            await b.call('Page.navigate',{'url':origin+'/'})
            await b.wait_for("document.querySelectorAll('[data-field]').length===12")
            assert await b.evaluate("document.querySelectorAll('.library-card').length===0 && document.querySelectorAll('.journey-links a').length===4")
            await b.evaluate("document.querySelector('#careers').scrollIntoView()")
            await b.screenshot(f'task2-library-{width}.png')
            await b.evaluate("document.querySelector('[data-field=technology]').click()")
            await b.wait_for("document.querySelectorAll('.library-card').length===12")
            await b.screenshot(f'task2-list-{width}.png')
            await b.evaluate("document.querySelector('.library-card').click()")
            await b.wait_for("Boolean(document.querySelector('.library-modal-actions'))")
            assert await b.evaluate("document.querySelector('.library-modal-actions a').href.includes('career_id=lap-trinh')")
            await b.screenshot(f'task2-modal-{width}.png')
            await b.evaluate("document.querySelector('#content-dialog').close();document.querySelector('#library-reset').click();document.querySelector('#career-search').value='bac si';document.querySelector('#search-form').requestSubmit()")
            await b.wait_for("document.querySelector('.library-card h3')?.textContent==='Bác sĩ'")
            assert await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            for mode in ('career_exploration','career_discovery'):
                await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode='+mode+('&career_id=bac-si' if mode.endswith('exploration') else '')})
                await b.wait_for("!document.querySelector('#career-survey').hidden && !document.querySelector('#survey-next').disabled")
                for i in range(5):
                    await b.evaluate("document.querySelector('#survey-answer').value='Em thích vẽ và tìm hiểu khoa học';document.querySelector('#survey-next').click()")
                await b.wait_for("document.querySelector('#career-survey').hidden")
                if mode.endswith('exploration'):
                    await b.wait_for("document.querySelector('#message-input').value.includes('Bác sĩ') && !document.querySelector('#send-message').disabled")
                    assert await b.evaluate("document.querySelectorAll('.message-row').length===1")
                    await b.call('Page.reload')
                    await b.wait_for("document.querySelector('#message-input').value.includes('Bác sĩ') && !document.querySelector('#send-message').disabled")
                    await b.screenshot(f'task2-exploration-draft-{width}.png')
                    await b.evaluate("document.querySelector('#message-input').value+=' Em muốn biết cách chuẩn bị.';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#send-message').click()")
                await b.wait_for("document.querySelectorAll('.message-row').length===3 && !document.querySelector('#message-input').disabled")
                await b.screenshot(f'task2-{mode}-{width}.png')
                await b.call('Page.reload')
                await b.wait_for("document.querySelectorAll('.message-row').length===3")
                assert await b.evaluate("document.querySelector('#career-survey').hidden")
                if mode.endswith('exploration'):assert await b.evaluate("document.querySelector('#session-note').textContent.includes('Bác sĩ')")
            await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=ky-su-du-lieu'})
            await b.wait_for("!document.querySelector('#story-error').hidden")
            assert await b.evaluate("document.querySelector('#story-error').textContent.includes('đang được cập nhật') && document.querySelector('#story-content').hidden")
            await b.call('Page.navigate',{'url':origin+'/mot-ngay-lam-viec?nghe=bac-si'})
            await b.wait_for("!document.querySelector('#story-content').hidden")
        # Member fixture, not a real Firebase login.
        await b.evaluate("sessionStorage.setItem('__fixture_login','1')")
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor?mode=career_exploration&career_id=lap-trinh'})
        await b.wait_for("!document.querySelector('#career-survey').hidden && !document.querySelector('#survey-next').disabled")
        for i in range(5):await b.evaluate("document.querySelector('#survey-answer').value='Muốn tìm hiểu máy tính';document.querySelector('#survey-next').click()")
        await b.wait_for("document.querySelector('#message-input').value.includes('Lập trình viên')")
        await b.evaluate("document.querySelector('#send-message').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===3")
        await b.evaluate("document.querySelector('#logout').click()")
        await b.wait_for("location.pathname==='/'")
        assert not b.errors,b.errors
        print('PASS library/categories/cards/modal/search/story mapping; guest2modes/survey/edit draft/chat/reload; member chat/logout; desktop1440/mobile390; Firebase stub/AI demo/local PostgreSQL')


if __name__=='__main__':
    with LocalPostgres() as pg:
        with psycopg.connect(pg.url,autocommit=True) as db:
            for f in ('001_conversations.sql','002_guest_quota.sql'):db.execute((h.ROOT/'migrations'/f).read_text(encoding='utf-8'))
        os.environ['LABAN_BROWSER_TEST_DATABASE']=pg.url
        h.checks=checks;h.main()
