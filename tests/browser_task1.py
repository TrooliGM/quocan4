"""QA giới hạn Nhiệm vụ 1, Firebase stub + demo, chỉ database local riêng."""
import json
import websockets
import browser_smoke as harness


async def checks(debug_url, origin):
    async with websockets.connect(debug_url, max_size=20_000_000, origin='http://localhost:9227') as socket:
        b = harness.Browser(socket)
        await b.call('Runtime.enable'); await b.call('Page.enable')
        for width, height in ((1440,1000),(390,844)):
            await b.call('Emulation.setDeviceMetricsOverride', {'width':width,'height':height,'deviceScaleFactor':1,'mobile':width<600})
            await b.call('Page.navigate',{'url':origin+'/'})
            await b.wait_for("document.querySelectorAll('.career-card').length > 0")
            assert await b.evaluate("document.querySelectorAll('.journey-links a').length===4 && document.querySelector('.hero-actions #account-button') && document.querySelector('.hero-actions a').pathname==='/ai-career-advisor'")
            assert await b.evaluate("document.querySelector('.journey-nav').getBoundingClientRect().top >= document.querySelector('.hero').getBoundingClientRect().bottom-1")
            assert await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            await b.screenshot(f'task1-home-{width}.png')
            await b.evaluate("document.querySelector('#account-button').click()")
            await b.wait_for("document.querySelector('#auth-dialog').open")
            await b.evaluate("sessionStorage.setItem('__fixture_login','1')")
            await b.call('Page.navigate',{'url':origin+'/ai-career-advisor'})
            await b.wait_for("!document.querySelector('#chat-app').hidden")
            await b.evaluate("document.querySelector('#new-chat').click();document.querySelector('#remember-chat').checked=true;document.querySelector('#start-chat').click()")
            await b.wait_for("!document.querySelector('#career-survey').hidden")
            await b.evaluate("document.querySelector('#survey-suggestions button').click()")
            assert await b.evaluate("document.querySelector('#survey-answer').value.length>0")
            assert await b.evaluate("!document.querySelector('#survey-next').disabled")
            await b.evaluate("document.querySelector('#survey-answer').value='Em thích vẽ và máy tính';document.querySelector('#survey-answer').dispatchEvent(new Event('input'));document.querySelector('#survey-next').click()")
            await b.evaluate("document.querySelector('#survey-back').click()")
            assert await b.evaluate("document.querySelector('#survey-answer').value==='Em thích vẽ và máy tính'")
            await b.screenshot(f'task1-survey-{width}.png')
            assert await b.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            for step in range(5):
                await b.evaluate("document.querySelector('#survey-answer').value='Sáng tạo và kiên nhẫn';document.querySelector('#survey-next').click()")
            await b.wait_for("document.querySelector('#career-survey').hidden && document.querySelectorAll('.message-row').length===3")
            await b.call('Page.reload')
            await b.wait_for("!document.querySelector('#chat-app').hidden && document.querySelectorAll('.message-row').length===3")
            assert await b.evaluate("document.querySelector('#career-survey').hidden")
            await b.screenshot(f'task1-chat-{width}.png')
        assert not b.errors, b.errors
        print(json.dumps({'PASS':True,'viewports':[1440,390],'firebase':'stub','ai':'demo','database':'isolated local SQLite','checks':['home nav placement','login dialog','chat CTA','chips and free edit','back navigation','5-step submit','auto AI request','history reload without repeat survey','no overflow','no runtime exceptions']}))


if __name__ == '__main__':
    harness.checks = checks
    harness.main()
