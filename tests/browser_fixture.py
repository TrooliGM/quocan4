"""CHỈ CHO KIỂM THỬ: chạy qua browser_smoke.py trên loopback, không dùng để chạy web.

Thay Firebase bằng stub trong tiến trình kiểm thử; app.py không import module này.
"""
from fastapi import Header, HTTPException, Request
from fastapi.responses import Response
from fastapi.routing import APIRoute

import app as application
import advisor.routes as routes
from advisor.routes import require_user
import advisor.graph as graph

app = application.app


def fixture_user(authorization: str | None = Header(default=None), request: Request = None):
    if authorization is None and request is not None:
        from advisor.protection import server_guest
        return server_guest(request)
    if authorization and authorization.startswith(('Bearer browser-fixture-guest:', 'Bearer browser-fixture-linked:')):
        import re
        prefix,uid=authorization.split(':',1)
        if re.fullmatch(r'browser-guest-\d+',uid):
            return {'uid':uid,'provider':'anonymous' if prefix.endswith('guest') else 'password','display_name':'Bạn thử','email_verified':True}
    users = {
        'Bearer browser-fixture-only': {'uid':'browser-user','provider':'password'},
        'Bearer browser-fixture-guest': {'uid':'browser-guest','provider':'anonymous'},
        'Bearer browser-fixture-linked': {'uid':'browser-guest','provider':'password'},
    }
    if authorization not in users:
        raise HTTPException(401, "Fixture requires login")
    return {**users[authorization], "display_name": "Bạn thử", "email_verified": True}


app.dependency_overrides[require_user] = fixture_user
application.verify_user = lambda token: fixture_user("Bearer " + token)
routes.verify_user = application.verify_user
import os
if os.getenv('LABAN_BROWSER_TEST_LEGACY_AI') == '1':
    import ai
    import story_ai
    async def legacy_demo(state):
        return {'answer':'BẢN DEMO KIỂM THỬ · Thử tìm hiểu minh họa, thiết kế và lập trình.'}
    ai.advice_graph.ainvoke = legacy_demo
    story_ai.story_graph.ainvoke = legacy_demo
original_demo = graph.demo_reply


def demo_with_untrusted_html(state):
    data = original_demo(state)
    if state["message"] == "Kiểm tra nội dung không tin cậy":
        data["answer"] = '**Nội dung an toàn**\n\n<img src=x onerror="window.xssExecuted=true">\n\n[liên kết](javascript:alert(1))'
    return data


graph.demo_reply = demo_with_untrusted_html


def firebase_stub():
    return Response('''
const profile = {uid:'browser-user',isAnonymous:false,displayName:'Bạn thử',email:'test@example.com',emailVerified:true,getIdToken:async()=> 'browser-fixture-only'};
const guest = {uid:'browser-guest-'+(localStorage.getItem('__fixture_guest_serial')||'0'),isAnonymous:true,displayName:null,email:null,emailVerified:false,async getIdToken(){return (this.isAnonymous?'browser-fixture-guest:':'browser-fixture-linked:')+this.uid;}};
const stored=sessionStorage.getItem('__fixture_login');
if(stored==='linked')guest.isAnonymous=false;
const auth = {currentUser:stored==='1'?profile:['guest','linked'].includes(stored)?guest:null};
const listeners = new Set();
const update=(user,state)=>{auth.currentUser=user;sessionStorage.setItem('__fixture_login',state);listeners.forEach(cb=>cb(user));return {user};};
const sdk = {
  async getRedirectResult(){if(sessionStorage.getItem('__fixture_redirect')==='1'){sessionStorage.removeItem('__fixture_redirect');return {user:profile};}return null;},
  browserLocalPersistence:{}, browserSessionPersistence:{}, setPersistence:async()=>{},
  onAuthStateChanged(a,callback) { listeners.add(callback); queueMicrotask(()=>callback(a.currentUser)); return ()=>listeners.delete(callback); },
  async signInWithEmailAndPassword() {auth.currentUser=profile;sessionStorage.setItem('__fixture_login','1');listeners.forEach(cb=>cb(profile));return {user:profile};},
  async signInAnonymously(){const n=Number(localStorage.getItem('__fixture_guest_serial')||0)+1;localStorage.setItem('__fixture_guest_serial',String(n));guest.uid='browser-guest-'+n;return update(guest,'guest');},
  EmailAuthProvider: {credential:(email,password)=>({email,password})},
  async linkWithCredential(user){user.isAnonymous=false;return update(user,'linked');},
  async createUserWithEmailAndPassword(){return update(profile,'1');},
  async updateProfile(user,data){Object.assign(user,data);},
  async sendEmailVerification(){},
  async linkWithPopup(user){
    if(sessionStorage.getItem('__fixture_google_existing')==='1')throw {code:'auth/credential-already-in-use',credential:{}};
    user.isAnonymous=false;return update(user,'linked');
  },
  GoogleAuthProvider: class {setCustomParameters(){} static credentialFromError(e){return e.credential;}},
  async signInWithCredential(){return update(profile,'1');},
  async signInWithPopup() {if(sessionStorage.getItem('__fixture_cancel_google')==='1')throw {code:'auth/popup-closed-by-user'};auth.currentUser=profile;sessionStorage.setItem('__fixture_login','1');listeners.forEach(cb=>cb(profile));return {user:profile};},
  async signOut() {auth.currentUser=null;sessionStorage.removeItem('__fixture_login');listeners.forEach(cb=>cb(null));}
};
export async function getFirebase(){if(new URLSearchParams(location.search).has('fixture_no_firebase'))throw new Error('Firebase unavailable fixture');return {auth,sdk};}
export async function restoredUser(){return auth.currentUser;}
''', media_type="application/javascript")


app.router.routes.insert(0, APIRoute("/assets/firebase-client.js", firebase_stub, methods=["GET"]))

if os.getenv('LABAN_BROWSER_ADVISOR30')=='1':
    from browser_advisor30_fixture import install
    install()
