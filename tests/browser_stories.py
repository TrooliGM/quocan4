"""Chrome: luồng truyện thật, AI giả lập; không gọi dịch vụ trả phí."""
import asyncio
import websockets
import browser_smoke as harness


async def checks(debug_url, origin):
    async with websockets.connect(debug_url, max_size=20_000_000, origin='http://localhost:9227') as socket:
        browser = harness.Browser(socket)
        await browser.call('Runtime.enable')
        await browser.call('Page.enable')
        await browser.call('Emulation.setDeviceMetricsOverride', {'width': 1440, 'height': 1100, 'deviceScaleFactor': 1, 'mobile': False})
        await browser.call('Page.addScriptToEvaluateOnNewDocument', {'source': """
const realFetch=window.fetch;
window.storyTest={calls:[],mode:'ok'};
window.fetch=async(url,options)=>{
 if(String(url).includes('/api/career-stories/') && String(url).endsWith('/ask')){
  storyTest.calls.push({url,body:JSON.parse(options.body)});
  if(storyTest.mode==='slow') await new Promise(resolve=>storyTest.finish=resolve);
  return new Response(JSON.stringify({answer:'Gợi ý thử nghiệm <img src=x onerror="window.xss=true">'}),{status:200,headers:{'Content-Type':'application/json'}});
 }
 return realFetch(url,options);
};
"""})
        await browser.call('Page.navigate', {'url': origin + '/mot-ngay-lam-viec?nghe=bac-si'})
        await browser.wait_for("!document.querySelector('#story-content')?.hidden && document.querySelectorAll('[data-career-id]').length===6")
        await browser.wait_for("document.fonts.status==='loaded'")
        await browser.screenshot('stories-desktop.png')
        assert await browser.evaluate("document.querySelectorAll('#scene-art svg').length===1 && document.querySelector('#prev-scene').disabled")
        await browser.evaluate("document.querySelector('[data-choice=\"0\"]').click()")
        assert await browser.evaluate("!document.querySelector('#decision-feedback').hidden")
        await browser.evaluate("document.querySelector('#next-scene').click(); document.querySelector('#prev-scene').click()")
        assert await browser.evaluate("document.querySelector('[data-choice=\"0\"]').getAttribute('aria-pressed')==='true'")
        await browser.evaluate("document.querySelector('#player').focus()")
        await browser.call('Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 'ArrowRight'})
        assert await browser.evaluate("document.querySelector('#scene-time').textContent==='10:30'")
        await browser.evaluate("document.querySelector('#story-question').value='Hội chẩn cần kỹ năng gì?'; document.querySelector('#story-ask-form').requestSubmit()")
        await browser.wait_for("document.querySelector('#story-answer').textContent.includes('Gợi ý thử nghiệm')")
        assert await browser.evaluate("storyTest.calls[0].body.scene_index===1 && !window.xss && !document.querySelector('#story-answer img')")
        # Response from a previous scene must not appear after changing careers.
        await browser.evaluate("storyTest.mode='slow'; document.querySelector('#story-ask-form').requestSubmit()")
        await browser.wait_for("!!storyTest.finish")
        await browser.evaluate("document.querySelector('[data-career-id=lap-trinh]').click()")
        await browser.wait_for("document.querySelector('#career-title').textContent.includes('lập trình') && !document.querySelector('#story-content').hidden")
        await browser.evaluate("storyTest.finish()")
        await asyncio.sleep(.2)
        assert await browser.evaluate("document.querySelector('#story-answer').hidden")
        # Autoplay actually advances, and pause stops the scheduled next scene.
        await browser.evaluate("document.querySelector('#scene-speed').insertAdjacentHTML('beforeend','<option value=250>test</option>'); document.querySelector('#scene-speed').value='250'; document.querySelector('#play-toggle').click()")
        await browser.wait_for("document.querySelector('#scene-counter').textContent==='Cảnh 2 / 4'")
        await browser.evaluate("document.querySelector('#play-toggle').click()")
        await asyncio.sleep(.5)
        assert await browser.evaluate("document.querySelector('#scene-counter').textContent==='Cảnh 2 / 4'")
        await browser.evaluate("document.querySelector('[data-scene=\"3\"]').click(); document.querySelector('#next-scene').click()")
        assert await browser.evaluate("!document.querySelector('#day-summary').hidden")
        await browser.evaluate("document.querySelector('#restart-story').click(); document.querySelector('#mode-comic').click()")
        assert await browser.evaluate("document.querySelectorAll('.comic-panel').length===4 && document.querySelector('#player').hidden")
        await browser.screenshot('stories-comic.png')
        for career in ['thiet-ke','giao-vien','ky-su-moi-truong','truyen-thong','bac-si']:
            await browser.evaluate(f"document.querySelector('[data-career-id={career}]').click()")
            await browser.wait_for(f"!document.querySelector('#story-content').hidden && location.search.includes('{career}')")
            assert await browser.evaluate("document.querySelectorAll('.comic-art svg').length===4")
        await browser.evaluate("document.querySelector('[data-open-scene=\"0\"]').click()")
        await browser.call('Emulation.setDeviceMetricsOverride', {'width': 390, 'height': 844, 'deviceScaleFactor': 1, 'mobile': True})
        await browser.evaluate("document.querySelector('#player').scrollIntoView({block:'start'})")
        await browser.screenshot('stories-mobile.png')
        assert await browser.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'Mobile overflow'
        await browser.call('Emulation.setEmulatedMedia', {'features': [{'name': 'prefers-reduced-motion', 'value': 'reduce'}]})
        assert await browser.evaluate("getComputedStyle(document.querySelector('#scene-art .moving-hand')).animationName==='none'")
        await browser.call('Page.navigate', {'url': origin + '/mot-ngay-lam-viec?nghe=unknown'})
        await browser.wait_for("!document.querySelector('#story-error')?.hidden")
        await browser.evaluate("document.querySelector('[data-career-id=bac-si]').click()")
        await browser.wait_for("!document.querySelector('#story-content')?.hidden")
        # Homepage entry points and mobile layout.
        await browser.call('Page.navigate', {'url': origin + '/'})
        await browser.wait_for("document.querySelectorAll('.career-story-link').length===3")
        assert await browser.evaluate("!!document.querySelector('.story-feature a[href*=bac-si]') && document.documentElement.scrollWidth<=innerWidth")
        await browser.call('Emulation.setDeviceMetricsOverride', {'width': 900, 'height': 900, 'deviceScaleFactor': 1, 'mobile': False})
        assert await browser.evaluate("document.documentElement.scrollWidth<=innerWidth"), 'Tablet homepage overflow'
        await browser.evaluate("document.querySelector('#menu-toggle').click()")
        assert await browser.evaluate("document.querySelector('#nav-links').classList.contains('open')")
        assert not browser.errors, browser.errors
        print('PASS: six stories, scenes, answers, keyboard, autoplay/pause, comic, summary, AI context/stale response/XSS, mobile, reduced motion, unknown career, homepage links')


if __name__ == '__main__':
    harness.checks = checks
    harness.main()
