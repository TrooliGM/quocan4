"""CHỈ CHO KIỂM THỬ: chạy qua browser_smoke.py trên loopback, không dùng để chạy web.

Thay Firebase bằng stub trong tiến trình kiểm thử; app.py không import module này.
"""
from fastapi import Header, HTTPException
from fastapi.responses import Response
from fastapi.routing import APIRoute

import app as application
from advisor.routes import require_user
import advisor.graph as graph

app = application.app


def fixture_user(authorization: str | None = Header(default=None)):
    if authorization != "Bearer browser-fixture-only":
        raise HTTPException(401, "Fixture requires login")
    return {"uid": "browser-user", "display_name": "Bạn thử", "email_verified": True}


app.dependency_overrides[require_user] = fixture_user
application.verify_user = lambda token: fixture_user("Bearer " + token)
original_demo = graph.demo_reply


def demo_with_untrusted_html(state):
    data = original_demo(state)
    if state["message"] == "Kiểm tra nội dung không tin cậy":
        data["answer"] = '**Nội dung an toàn**\n\n<img src=x onerror="window.xssExecuted=true">\n\n[liên kết](javascript:alert(1))'
    return data


graph.demo_reply = demo_with_untrusted_html


def firebase_stub():
    return Response('''
const profile = {uid:'browser-user',displayName:'Bạn thử',email:'test@example.com',emailVerified:true,getIdToken:async()=> 'browser-fixture-only'};
const auth = {currentUser:sessionStorage.getItem('__fixture_login')==='1'?profile:null};
const listeners = new Set();
const sdk = {
  browserLocalPersistence:{}, browserSessionPersistence:{}, setPersistence:async()=>{},
  onAuthStateChanged(a,callback) { listeners.add(callback); queueMicrotask(()=>callback(a.currentUser)); return ()=>listeners.delete(callback); },
  async signInWithEmailAndPassword() {auth.currentUser=profile;sessionStorage.setItem('__fixture_login','1');listeners.forEach(cb=>cb(profile));return {user:profile};},
  async signOut() {auth.currentUser=null;sessionStorage.removeItem('__fixture_login');listeners.forEach(cb=>cb(null));}
};
export async function getFirebase(){return {auth,sdk};}
export async function restoredUser(){return auth.currentUser;}
''', media_type="application/javascript")


app.router.routes.insert(0, APIRoute("/assets/firebase-client.js", firebase_stub, methods=["GET"]))
