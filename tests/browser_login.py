"""Kiểm tra đăng nhập mở thẳng chat bằng Firebase giả lập."""
import asyncio
import websockets
import browser_smoke as harness


async def checks(debug_url, origin):
    async with websockets.connect(debug_url, max_size=20_000_000, origin='http://localhost:9227') as socket:
        browser = harness.Browser(socket)
        await browser.call('Runtime.enable')
        await browser.call('Page.enable')
        await browser.call('Page.addScriptToEvaluateOnNewDocument', {'source': """
const originalFetch=window.fetch;
window.blockProfile=false;
window.fetch=(url,options)=>{
 if(window.blockProfile && String(url)==='/api/auth/me') return Promise.resolve(new Response(JSON.stringify({detail:'test unavailable'}),{status:503}));
 if(String(url)==='/api/ai/sessions' && options?.method==='POST'){
  sessionStorage.setItem('testSessionCreates',String(Number(sessionStorage.getItem('testSessionCreates')||0)+1));
  sessionStorage.setItem('testSessionRemember',JSON.parse(options.body).remember);
 }
 return originalFetch(url,options);
};
"""})
        await browser.call('Page.navigate', {'url': origin + '/'})
        await browser.wait_for("!document.querySelector('#auth-submit')?.disabled")
        await browser.evaluate("document.querySelector('[data-open-auth]').click(); window.blockProfile=true; document.querySelector('#auth-email').value='test@example.com'; document.querySelector('#auth-password').value='test-password'; document.querySelector('#auth-form').requestSubmit()")
        await browser.wait_for("document.querySelector('#auth-status').classList.contains('error') && !document.querySelector('#auth-submit').disabled")
        assert await browser.evaluate("location.pathname==='/' && !sessionStorage.getItem('testSessionCreates')"), 'Backend failure must not open chat'
        await browser.evaluate("sessionStorage.clear()")
        await browser.call('Page.reload')
        await browser.wait_for("!document.querySelector('#auth-submit')?.disabled")
        await browser.evaluate("document.querySelector('[data-open-auth]').click(); document.querySelector('#auth-email').value='test@example.com'; document.querySelector('#auth-password').value='test-password'; document.querySelector('#auth-form').requestSubmit()")
        await browser.wait_for("location.pathname==='/ai-career-advisor' && document.querySelectorAll('.message-row').length===1 && document.activeElement.id==='message-input' && !location.search")
        assert await browser.evaluate("document.querySelector('#welcome').hidden && sessionStorage.getItem('testSessionRemember')==='false' && sessionStorage.getItem('testSessionCreates')==='1'")
        # An existing sign-in opened through the login link restores the same conversation.
        await browser.call('Page.navigate', {'url': origin + '/?login=1'})
        await browser.wait_for("location.pathname==='/ai-career-advisor' && document.querySelectorAll('.message-row').length===1 && !location.search")
        assert await browser.evaluate("sessionStorage.getItem('testSessionCreates')==='1'")
        # Navigating home intentionally is still possible for signed-in users.
        await browser.call('Page.navigate', {'url': origin + '/'})
        await browser.wait_for("document.querySelector('#account-label')?.textContent==='Tài khoản'")
        await browser.evaluate("sessionStorage.clear()")
        await browser.call('Page.reload')
        await browser.wait_for("!document.querySelector('#google-signin')?.disabled")
        await browser.evaluate("document.querySelector('[data-open-auth]').click(); document.querySelector('#google-signin').click()")
        await browser.wait_for("location.pathname==='/ai-career-advisor' && document.querySelectorAll('.message-row').length===1 && document.activeElement.id==='message-input' && !location.search")
        assert await browser.evaluate("document.querySelector('#welcome').hidden && sessionStorage.getItem('testSessionRemember')==='false' && sessionStorage.getItem('testSessionCreates')==='1'")
        await browser.call('Page.reload')
        await browser.wait_for("document.querySelectorAll('.message-row').length===1")
        assert await browser.evaluate("sessionStorage.getItem('testSessionCreates')==='1'"), 'Refresh must not create duplicate sessions'
        assert not browser.errors, browser.errors
        print('PASS: email/Google open chat directly, input focus, temporary consent, restored session, no duplicate on refresh, backend failure, homepage access')


if __name__ == '__main__':
    harness.checks = checks
    harness.main()
