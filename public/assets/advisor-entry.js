// Compatibility for cached pre-unification HTML. Presentation grants no data access.
try{
  const response=await fetch('/ai-career-advisor',{cache:'no-store',signal:AbortSignal.timeout(12000)});
  if(!response.ok)throw Error('shell unavailable');
  const parsed=new DOMParser().parseFromString(await response.text(),'text/html');
  document.title=parsed.title;document.body.replaceWith(parsed.body);
  const css=[...document.querySelectorAll('link[rel=stylesheet]')].find(l=>l.href.includes('stable-chat.css'));
  if(css)css.href='/assets/chat.css?v=task44-journey-2';
  await import('./chat.js?v=task44-finalqa-1');
}catch{
  const message=document.createElement('p');message.textContent='Chưa mở được cuộc trò chuyện. Bạn hãy tải lại trang để thử lại.';
  document.body.replaceChildren(message); // Never silently select an older AI/UI.
}
