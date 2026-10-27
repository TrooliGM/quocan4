"""Chrome + PostgreSQL local + Firebase/AI giả lập: khách và nâng cấp tài khoản."""
import os
import websockets
from urllib.parse import quote
from unittest.mock import patch
import browser_smoke as harness
from postgres_fixture import LocalPostgres


async def checks(debug_url,origin):
    async with websockets.connect(debug_url,max_size=20_000_000,origin='http://localhost:9227') as socket:
        b=harness.Browser(socket)
        await b.call('Runtime.enable');await b.call('Page.enable')
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor'})
        await b.wait_for("document.querySelectorAll('.message-row').length===1 && !document.querySelector('#guest-banner').hidden && !document.querySelector('#start-chat').disabled")
        assert await b.evaluate("location.pathname==='/ai-career-advisor' && document.querySelector('#guest-quota-text').textContent.includes('8/8')")
        for i in range(8):
            await b.evaluate(f"document.querySelector('#message-input').value='Mình thích vẽ {i}';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
            await b.wait_for(f"document.querySelectorAll('.message-row').length==={3+2*i} && document.querySelector('#thinking').hidden")
        assert await b.evaluate("document.querySelector('#guest-banner').classList.contains('limit-reached') && document.querySelector('#send-message').disabled")
        await b.screenshot('guest-quota-eight.png')
        await b.evaluate("document.querySelector('#message-input').value='Câu thứ chín';document.querySelector('#message-form').requestSubmit()")
        assert await b.evaluate("document.querySelectorAll('.message-row.user').length===8")
        # Liên kết email mới giữ nguyên Firebase UID và lịch sử.
        await b.evaluate("document.querySelector('#guest-login').click()")
        await b.wait_for("document.querySelector('#auth-dialog')?.open && !document.querySelector('#auth-submit').disabled")
        await b.evaluate("document.querySelector('#mode-register').click();document.querySelector('#auth-name').value='Bạn thử';document.querySelector('#auth-email').value='new@example.com';document.querySelector('#auth-password').value='test-password';document.querySelector('#auth-confirm-password').value='test-password';document.querySelector('#auth-form').requestSubmit()")
        await b.wait_for("location.pathname==='/ai-career-advisor' && document.querySelectorAll('.message-row').length===17 && document.querySelector('#guest-banner').hidden")
        assert await b.evaluate("sessionStorage.getItem('__fixture_login')==='linked'")
        await b.evaluate("document.querySelector('#message-input').value='Tiếp tục sau nâng cấp';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
        await b.wait_for("document.querySelectorAll('.message-row').length===19 && document.querySelector('#thinking').hidden")
        # Tạo UID khách mới trong fixture để thử Google đã có tài khoản.
        await b.evaluate("sessionStorage.clear()")
        await b.call('Page.navigate',{'url':origin+'/ai-career-advisor'})
        await b.wait_for("!document.querySelector('#guest-banner')?.hidden && !document.querySelector('#chat-app').hidden && document.querySelectorAll('.message-row').length===1 && !document.querySelector('#start-chat').disabled")
        await b.evaluate("document.querySelector('#message-input').value='Lịch sử khách trước Google';document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
        await b.wait_for("document.querySelectorAll('.message-row').length===3 && document.querySelector('#thinking').hidden")
        await b.evaluate("sessionStorage.setItem('__fixture_google_existing','1');document.querySelector('#guest-login').click()")
        await b.wait_for("document.querySelector('#auth-dialog')?.open && !document.querySelector('#google-signin').disabled")
        await b.evaluate("window.realFetch=window.fetch;window.fetch=(url,options)=>String(url)==='/api/ai/guest/claim'?Promise.resolve(new Response('{}',{status:503})):realFetch(url,options)")
        await b.evaluate("document.querySelector('#google-signin').click()")
        await b.wait_for("document.querySelector('#auth-status').classList.contains('error') && !document.querySelector('#auth-submit').disabled")
        assert await b.evaluate("location.pathname==='/' && [...document.querySelectorAll('button')].some(x=>x.textContent==='Thử giữ lịch sử' && !x.hidden)")
        await b.evaluate("window.fetch=window.realFetch;[...document.querySelectorAll('button')].find(x=>x.textContent==='Thử giữ lịch sử').click()")
        await b.wait_for("location.pathname==='/ai-career-advisor' && document.querySelectorAll('.message-row').length===3 && document.querySelector('#guest-banner').hidden")
        assert await b.evaluate("document.querySelector('#messages').textContent.includes('Lịch sử khách trước Google')")
        await b.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
        assert await b.evaluate("document.documentElement.scrollWidth<=innerWidth")
        assert not b.errors,b.errors
        print('PASS: anonymous chat 1-8, ninth blocked, email link keeps UID/history, continues after eight, existing Google claim failure/retry keeps history, mobile')


if __name__=='__main__':
    with LocalPostgres() as cluster:
        db=cluster.schema()
        url=cluster.url+'?options='+quote('-c search_path='+db.schema_name)
        with patch.dict(os.environ,{'LABAN_BROWSER_TEST_DATABASE':url}):
            harness.checks=checks;harness.main()
