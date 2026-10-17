"""Kiểm tra nút Truyện nghề trong chat; chỉ dùng Firebase/AI giả lập và SQLite test."""
import asyncio
import websockets
import browser_smoke as harness


async def checks(debug_url, origin):
    async with websockets.connect(debug_url,max_size=20_000_000,origin='http://localhost:9227') as socket:
        b=harness.Browser(socket)
        await b.call('Runtime.enable')
        await b.call('Page.enable')
        await b.call('Emulation.setDeviceMetricsOverride',{'width':1440,'height':1000,'deviceScaleFactor':1,'mobile':False})
        await b.call('Page.addScriptToEvaluateOnNewDocument',{'source':"""
const safeTestFetch=window.fetch;
window.fetch=async(url,options)=>{
 const response=await safeTestFetch(url,options);
 if(sessionStorage.getItem('__story_tamper')==='1'&&String(url).startsWith('/api/ai/sessions/')&&(!options?.method||options.method==='GET')){
  const data=await response.clone().json();
  if(data.session?.messages?.length){
   data.session.messages.at(-1).story_navigation={kind:'open',choices:[
    {career_id:'bac-si',career_name:'<img src=x onerror="window.storyXss=1">',href:'https://evil.example/'},
    {career_id:'../../evil',career_name:'bad',href:'javascript:alert(1)'}]};
   return new Response(JSON.stringify(data),{status:response.status,headers:{'Content-Type':'application/json'}});
  }
 }
 return response;
};
"""})
        await b.call('Page.navigate',{'url':origin+'/?login=1'})
        await b.wait_for("document.querySelector('#auth-dialog')?.open&&!document.querySelector('#auth-submit').disabled")
        await b.evaluate("document.querySelector('#auth-email').value='test@example.com';document.querySelector('#auth-password').value='test-password';document.querySelector('#auth-form').requestSubmit()")
        await b.wait_for("location.pathname==='/ai-career-advisor'&&!document.querySelector('#chat-app')?.hidden&&document.querySelectorAll('.message-row').length===1")
        await b.evaluate("document.querySelector('#new-chat').click();document.querySelector('#remember-chat').checked=true;document.querySelector('#start-chat').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===1&&!document.querySelector('#start-chat').disabled")

        async def send(message):
            import json
            before=await b.evaluate("document.querySelectorAll('.message-row').length")
            await b.evaluate("document.querySelector('#message-input').value="+json.dumps(message)+";document.querySelector('#message-input').dispatchEvent(new Event('input'));document.querySelector('#message-form').requestSubmit()")
            await b.wait_for(f"document.querySelectorAll('.message-row').length==={before+2}&&document.querySelector('#thinking').hidden")
            assert await b.evaluate("location.pathname==='/ai-career-advisor'"),'Must never auto-navigate'

        await send('Một ngày làm việc của bác sĩ như thế nào?')
        await b.wait_for("document.querySelector('.message-row:last-child .story-experience-link')?.getAttribute('href')==='/mot-ngay-lam-viec?nghe=bac-si'")
        assert await b.evaluate("document.querySelector('.message-row:last-child .story-experience-link').textContent==='Khám phá một ngày làm việc →'")
        saved=await b.evaluate("({id:sessionStorage.getItem('laban.advisor.browser-user'),text:document.querySelector('#messages').innerText})")
        await b.screenshot('story-intent-desktop.png')
        await b.evaluate("document.querySelector('.message-row:last-child .story-experience-link').click()")
        await b.wait_for("location.pathname==='/mot-ngay-lam-viec'&&location.search==='?nghe=bac-si'&&!document.querySelector('#story-content')?.hidden")
        assert await b.evaluate("document.querySelector('#career-title').textContent.toLowerCase().includes('bác sĩ')")
        await b.evaluate("document.querySelector('a[href=\"/ai-career-advisor\"]').click()")
        await b.wait_for("location.pathname==='/ai-career-advisor'&&document.querySelectorAll('.message-row').length===3&&!!document.querySelector('.story-experience-link')")
        assert await b.evaluate("sessionStorage.getItem('laban.advisor.browser-user')")==saved['id']
        assert await b.evaluate("document.querySelector('#messages').innerText")==saved['text']

        for message,key in [('Cho mình trải nghiệm một ngày làm lập trình viên.','lap-trinh'),('Giáo viên thường làm những gì mỗi ngày?','giao-vien')]:
            await send(message)
            await b.wait_for(f"document.querySelector('.message-row:last-child .story-experience-link')?.getAttribute('href')==='/mot-ngay-lam-viec?nghe={key}'")
        for message,phrase in [('Mình muốn biết lịch trình của kiến trúc sư.','chưa có nội dung'),
                               ('Mình muốn xem một ngày làm việc','Bạn muốn khám phá một ngày làm việc của nghề nào?'),
                               ('Một ngày làm người chăm sóc kỳ lân?','chưa có nội dung')]:
            await send(message)
            assert await b.evaluate("document.querySelector('.message-row:last-child').innerText.includes("+__import__('json').dumps(phrase)+")")
            assert not await b.evaluate("!!document.querySelector('.message-row:last-child .story-experience-link')")
        for message in ['Lương của lập trình viên bao nhiêu?','Không muốn xem truyện, cứ trả lời về một ngày làm bác sĩ trong chat thôi.']:
            await send(message)
            assert not await b.evaluate("!!document.querySelector('.message-row:last-child .story-experience-link')")
        await send('Một ngày làm việc của bác sĩ và kỹ sư phần mềm khác nhau thế nào?')
        await b.wait_for("document.querySelectorAll('.message-row:last-child .story-experience-link').length===2")

        # Không tin href/tên/ID giả mạo kể cả khi bị chèn vào phản hồi lịch sử.
        await b.evaluate("sessionStorage.setItem('__story_tamper','1')")
        await b.call('Page.reload')
        await b.wait_for("!document.querySelector('#chat-app')?.hidden&&!!document.querySelector('.message-row:last-child .story-experience-link')")
        assert await b.evaluate("document.querySelectorAll('.message-row:last-child .story-experience-link').length===1")
        assert await b.evaluate("document.querySelector('.message-row:last-child .story-experience-link').getAttribute('href')==='/mot-ngay-lam-viec?nghe=bac-si'&&!window.storyXss")
        await b.evaluate("sessionStorage.removeItem('__story_tamper')")
        await b.call('Page.reload')
        await b.wait_for("document.querySelectorAll('.message-row:last-child .story-experience-link').length===2")
        await b.call('Emulation.setDeviceMetricsOverride',{'width':390,'height':844,'deviceScaleFactor':1,'mobile':True})
        assert await b.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
        await b.screenshot('story-intent-mobile.png')
        await b.call('Page.navigate',{'url':origin+'/'})
        await b.wait_for("!!document.querySelector('#nav-links a[href=\"/mot-ngay-lam-viec\"]')")
        await b.evaluate("document.querySelector('#menu-toggle').click();document.querySelector('#nav-links a[href=\"/mot-ngay-lam-viec\"]').click()")
        await b.wait_for("location.pathname==='/mot-ngay-lam-viec'&&!document.querySelector('#story-content')?.hidden")
        await b.evaluate("document.querySelector('a[href=\"/ai-career-advisor\"]').click()")
        await b.wait_for("!document.querySelector('#chat-app')?.hidden&&document.querySelectorAll('.message-row').length>1")
        await b.evaluate("document.querySelector('#new-chat').click();document.querySelector('#remember-chat').checked=false;document.querySelector('#start-chat').click()")
        await b.wait_for("document.querySelectorAll('.message-row').length===1&&!document.querySelector('#start-chat').disabled")
        await send('Một ngày làm lập trình viên ra sao?')
        await b.wait_for("!!document.querySelector('.message-row:last-child .story-experience-link')")
        temporary=await b.evaluate("sessionStorage.getItem('laban.advisor.browser-user')")
        await b.evaluate("document.querySelector('.message-row:last-child .story-experience-link').click()")
        await b.wait_for("location.search==='?nghe=lap-trinh'&&!document.querySelector('#story-content')?.hidden")
        await b.evaluate("document.querySelector('a[href=\"/ai-career-advisor\"]').click()")
        await b.wait_for("location.pathname==='/ai-career-advisor'&&document.querySelectorAll('.message-row').length===3")
        assert await b.evaluate("sessionStorage.getItem('laban.advisor.browser-user')")==temporary
        assert not b.errors,b.errors
        print('PASS: daily intents/aliases, missing and unknown career, salary/refusal, multi-choice, safe URLs, click-only story navigation, preserved history, mobile and Navbar')


if __name__=='__main__':
    harness.checks=checks
    harness.main()
