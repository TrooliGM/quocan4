"""Kiểm thử Chrome headless với Firebase stub; không gửi dữ liệu tới provider thật.

Chạy: python tests/browser_smoke.py. Cần Chrome và package websockets cho công cụ test này.
"""
import asyncio
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from uuid import uuid4

import websockets

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"

class Browser:
    def __init__(self, socket):
        self.socket = socket
        self.sequence = 0
        self.errors = []

    async def call(self, method, params=None):
        self.sequence += 1
        identifier = self.sequence
        await self.socket.send(json.dumps({"id":identifier, "method":method, "params":params or {}}))
        while True:
            message = json.loads(await self.socket.recv())
            if message.get("method") == "Runtime.exceptionThrown":
                self.errors.append(message["params"]["exceptionDetails"])
            if message.get("id") == identifier:
                if "error" in message: raise RuntimeError(message["error"])
                return message.get("result", {})

    async def evaluate(self, expression):
        data = await self.call("Runtime.evaluate", {"expression":expression, "awaitPromise":True, "returnByValue":True})
        if data.get("exceptionDetails"): raise AssertionError(data["exceptionDetails"])
        return data.get("result", {}).get("value")

    async def wait_for(self, expression, timeout=20):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if await self.evaluate(expression): return
            await asyncio.sleep(.15)
        raise AssertionError("Timed out: " + expression + "\n" + str(await self.evaluate("JSON.stringify({url:location.href,state:document.readyState,body:document.body?.innerText})")) + "\n" + str(self.errors))

    async def screenshot(self, name):
        result = await self.call("Page.captureScreenshot", {"format":"png"})
        (ARTIFACTS / name).write_bytes(base64.b64decode(result["data"]))


async def checks(debug_url, origin):
    async with websockets.connect(debug_url, max_size=20_000_000, origin="http://localhost:9227") as socket:
        browser = Browser(socket)
        await browser.call("Runtime.enable")
        await browser.call("Page.enable")
        await browser.call("Emulation.setDeviceMetricsOverride", {"width":1440, "height":1000, "deviceScaleFactor":1, "mobile":False})
        # Khách mở trang chat phải quay về hộp đăng nhập hiện có.
        await browser.call("Page.navigate", {"url":origin + "/?login=1"})
        await browser.wait_for("location.search.includes('login=1') && document.querySelector('#auth-dialog')?.open")
        await browser.wait_for("!document.querySelector('#auth-submit').disabled")
        await browser.evaluate("document.querySelector('#auth-email').value='test@example.com'; document.querySelector('#auth-password').value='test-password'; document.querySelector('#auth-form').requestSubmit()")
        await browser.wait_for("location.pathname==='/ai-career-advisor' && !document.querySelector('#chat-app')?.hidden")
        await browser.wait_for("document.fonts.status==='loaded'")
        await browser.wait_for("document.querySelector('#welcome').hidden && document.querySelectorAll('.message-row').length===1 && document.activeElement.id==='message-input'")
        # Sau đăng nhập đã vào chat; mở phiên mới để kiểm tra lựa chọn lưu chủ động.
        await browser.evaluate("document.querySelector('#new-chat').click()")
        await browser.screenshot("advisor-desktop-welcome.png")
        await browser.evaluate("document.querySelector('#remember-chat').checked=true; document.querySelector('#start-chat').click()")
        await browser.wait_for("document.querySelectorAll('.message-row').length===1 && !document.querySelector('#start-chat').disabled")
        await browser.evaluate("document.querySelector('#message-input').value='Mình thích Toán và vẽ'; document.querySelector('#message-input').dispatchEvent(new Event('input')); document.querySelector('#message-form').requestSubmit()")
        await browser.wait_for("document.querySelectorAll('.message-row').length===3 && document.querySelector('#thinking').hidden")
        assert await browser.evaluate("document.querySelector('#messages').innerText.includes('chưa gọi DeepSeek')")
        await browser.screenshot("advisor-desktop-chat.png")
        await browser.evaluate("document.querySelector('.history-item .icon-button').click()")
        await browser.wait_for("document.querySelector('#action-dialog').open")
        await browser.evaluate("document.querySelector('#rename-input').value='Hành trình Toán và vẽ'; document.querySelector('#action-form').requestSubmit()")
        await browser.wait_for("document.querySelector('.history-open strong')?.textContent==='Hành trình Toán và vẽ'")
        await browser.call("Page.reload")
        await browser.wait_for("document.querySelectorAll('.message-row').length===3")
        await browser.evaluate("document.querySelector('#message-input').value='Kiểm tra nội dung không tin cậy'; document.querySelector('#message-input').dispatchEvent(new Event('input')); document.querySelector('#message-form').requestSubmit()")
        await browser.wait_for("document.querySelectorAll('.message-row').length===5 && document.querySelector('#thinking').hidden")
        assert await browser.evaluate("!window.xssExecuted && !document.querySelector('.message-bubble img') && !document.querySelector('.message-bubble a[href^=\"javascript:\"]')")
        assert await browser.evaluate("!!window.marked && !!window.DOMPurify"), "CDN Markdown dependencies not available"
        await browser.evaluate("document.querySelector('#open-profile').click()")
        await browser.wait_for("document.querySelector('#profile-dialog').open")
        await browser.evaluate("document.querySelector('#profile-dialog [data-close-dialog]').click()")
        await browser.call("Emulation.setDeviceMetricsOverride", {"width":390, "height":844, "deviceScaleFactor":1, "mobile":True})
        await browser.evaluate("document.querySelector('#new-chat').click()")
        await browser.wait_for("!document.querySelector('#welcome').hidden")
        await browser.wait_for("document.querySelector('#chat-scroll').scrollTop===0")
        assert await browser.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Mobile horizontal overflow"
        assert await browser.evaluate("document.querySelector('#start-chat').getBoundingClientRect().bottom <= document.querySelector('.composer-area').getBoundingClientRect().top"), "Mobile start button is below composer"
        await browser.screenshot("advisor-mobile-welcome.png")
        await browser.evaluate("document.querySelector('#open-sidebar').click()")
        assert await browser.evaluate("document.querySelector('#chat-sidebar').classList.contains('open')")
        await browser.screenshot("advisor-mobile-history.png")
        await browser.evaluate("document.querySelector('#close-sidebar').click(); document.querySelector('[data-prompt]').click()")
        await browser.wait_for("!document.querySelector('#messages').hidden && document.querySelector('#message-input').value.length>0")
        assert await browser.evaluate("!!document.querySelector('#microphone') && !document.querySelector('#voice-toggle, #voice-readiness, #audio-player, #voice-dialog')"), "Mic-only controls"
        assert await browser.evaluate("document.querySelector('#message-input').value.includes('công nghệ')")
        # Trình duyệt giả lập kết quả mic; cần 3 giây im lặng trước khi chép chữ.
        await browser.call("Page.addScriptToEvaluateOnNewDocument", {"source": """
window.micTest={aborted:0};
window.SpeechRecognition=class {
  start(){micTest.rec=this;queueMicrotask(()=>this.onstart?.());}
  stop(){this.onend?.();}
  abort(){micTest.aborted++;}
};
"""})
        await browser.call("Page.reload")
        await browser.wait_for("!document.querySelector('#chat-app')?.hidden && !document.querySelector('#microphone').disabled")
        await browser.evaluate("document.querySelector('#message-input').value='Mình thích'; document.querySelector('#message-input').dispatchEvent(new Event('input')); document.querySelector('#microphone').click()")
        await browser.wait_for("document.querySelector('#microphone').classList.contains('recording')")
        await browser.evaluate("micTest.rec.onresult({results:[[{transcript:'vẽ'}]]})")
        assert await browser.evaluate("document.querySelector('#message-input').value==='Mình thích' && document.querySelector('#send-message').disabled"), "Mic must wait for silence and manual Send"
        await browser.wait_for("document.querySelector('#message-input').value==='Mình thích vẽ' && !document.querySelector('#send-message').disabled", timeout=8)
        assert await browser.evaluate("document.querySelectorAll('.message-row.user').length===0"), "Transcript must not be sent automatically"
        await browser.evaluate("document.querySelector('#microphone').click()")
        await browser.wait_for("document.querySelector('#microphone').classList.contains('recording')")
        await browser.evaluate("window.lateMicResult=micTest.rec.onresult; document.querySelector('#cancel-mic').click(); lateMicResult({results:[[{transcript:'không lưu'}]]})")
        assert await browser.evaluate("document.querySelector('#message-input').value==='Mình thích vẽ' && micTest.aborted>0"), "Cancelled mic must not overwrite draft"
        await browser.evaluate("document.querySelector('#logout').click()")
        await browser.wait_for("location.pathname==='/' && !location.search")
        assert not browser.errors, browser.errors
        print("PASS: guest guard, demo chat, rename, restore, sanitized Markdown, profile, mobile drawer, mic silence/cancel/manual Send, logout")


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    chrome = Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe"
    suffix = uuid4().hex[:8]
    test_database = os.environ.get('LABAN_BROWSER_TEST_DATABASE')
    if test_database:
        from urllib.parse import urlparse
        if urlparse(test_database).hostname not in ('127.0.0.1','localhost'):
            raise RuntimeError('Browser PostgreSQL tests only accept loopback, never production.')
    environment = {**os.environ, "AI_DEMO_MODE":"true", "DATABASE_URL":test_database or "sqlite:///" + str(ARTIFACTS / f"browser-{suffix}.sqlite3")}
    with (ARTIFACTS / "browser-server.log").open("w", encoding="utf-8") as log, (ARTIFACTS / "browser-chrome.log").open("w", encoding="utf-8") as chrome_log:
        server = subprocess.Popen([sys.executable,"-m","uvicorn","browser_fixture:app","--app-dir","tests","--host","127.0.0.1","--port","8013","--no-proxy-headers"],
                                  cwd=ROOT, env=environment, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
        browser = subprocess.Popen([str(chrome),"--headless=new","--disable-gpu","--no-first-run","--no-default-browser-check","--no-proxy-server",
                                    "--remote-debugging-port=9227","--remote-allow-origins=http://localhost:9227",
                                    "--user-data-dir=" + str(ARTIFACTS / ("chrome-"+suffix)),"about:blank"],
                                   stdout=chrome_log, stderr=chrome_log, creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            tabs = None
            for _ in range(100):
                if browser.poll() is not None:
                    raise RuntimeError(f"Chrome exited: {browser.returncode}; inspect artifacts/browser-chrome.log")
                try:
                    urllib.request.urlopen("http://127.0.0.1:8013/api/health",timeout=1).close()
                    with urllib.request.urlopen("http://127.0.0.1:9227/json",timeout=1) as response:
                        tabs = [target for target in json.load(response) if target.get("type") == "page" and not target.get("url", "").startswith("chrome-extension:")]
                    if tabs: break
                except OSError: time.sleep(.15)
            if not tabs: raise RuntimeError("Chrome/server not ready; inspect artifacts/browser-server.log")
            asyncio.run(checks(tabs[0]["webSocketDebuggerUrl"],"http://127.0.0.1:8013"))
        finally:
            browser.terminate(); server.terminate()
            browser.wait(timeout=10); server.wait(timeout=10)


if __name__ == "__main__":
    main()
