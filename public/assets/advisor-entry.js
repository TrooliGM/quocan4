// Không tin UID/query do client tự khai. Server trả eligibility từ ID token thật.
import {getFirebase,restoredUser} from './firebase-client.js';
let eligible=false,token;
try{
  const {auth,sdk}=await getFirebase();const user=await restoredUser(auth,sdk);
  if(user&&!user.isAnonymous){
    token=await user.getIdToken();
    const response=await fetch('/api/ai/config',{headers:{Authorization:'Bearer '+token},cache:'no-store',signal:AbortSignal.timeout(12000)});
    if(response.ok){
      const data=await response.json();eligible=data.task4_enabled===true;
      window.__labanBootstrapConfig={uid:user.uid,data};
    }
  }
}catch{/* Giữ stable nếu không xác minh được eligibility. */}
if(eligible){
  const response=await fetch('/api/ai/task4-shell',{headers:{Authorization:'Bearer '+token},cache:'no-store'});
  if(response.ok){
    const parsed=new DOMParser().parseFromString(await response.text(),'text/html');
    document.title=parsed.title;document.body.replaceWith(parsed.body);
    const css=[...document.querySelectorAll('link[rel=stylesheet]')].find(l=>l.href.includes('stable-chat.css'));
    if(css)css.href='/assets/chat.css?v=task4-canary-1';
    await import('./chat.js?v=task4-canary-1');
  }else await import('./stable-chat.js?v=stable-df1c300');
}else await import('./stable-chat.js?v=stable-df1c300');
