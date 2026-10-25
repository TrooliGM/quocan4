// Render server-validated metadata. URL shape is checked again before DOM use.
export function keepVerifiedCitations(element,sources=[]) {
  const allowed=new Set();
  for(const source of Array.isArray(sources)?sources:[]){
    try{const url=new URL(source.url);if(url.protocol==='https:'&&!url.username&&!url.password)allowed.add(source.url);}catch{}
  }
  for(const link of element.querySelectorAll('a')){
    if(!allowed.has(link.getAttribute('href')))link.replaceWith(document.createTextNode(link.textContent));
    else{link.target='_blank';link.rel='noopener noreferrer';}
  }
}
export function navigationPath(kind,id) {
  if(id!==null && (typeof id!=='string'||!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id)||id.length>80))return null;
  if(kind==='career_profile')return id===null?'/#careers':'/?career='+id+'#careers';
  if(kind==='career_story')return id===null?'/mot-ngay-lam-viec':'/mot-ngay-lam-viec?nghe='+id;
  if(kind==='career_exploration'&&id)return '/ai-career-advisor?mode=career_exploration&career_id='+id;
  return null;
}
export function navigationButtons(items,beforeOpen=()=>{}) {
  if(!Array.isArray(items))return null;
  const group=document.createElement('nav');group.className='career-navigation';group.setAttribute('aria-label','Khám phá tiếp trong La Bàn');
  const seen=new Set();
  for(const item of items.slice(0,4)){
    if(!item||typeof item.label!=='string'||item.label.length>180)continue;
    const path=navigationPath(item.kind,item.career_id);
    if(!path||item.href!==path||seen.has(path))continue;
    seen.add(path);
    const link=document.createElement('a');link.className='career-navigation-link';link.href=path;link.target='_blank';link.rel='noopener noreferrer';
    link.setAttribute('aria-label',item.label+'. Mở trong tab mới');
    const label=document.createElement('span');label.textContent=item.label;
    const arrow=document.createElement('span');arrow.textContent='↗';arrow.setAttribute('aria-hidden','true');
    link.append(label,arrow);link.addEventListener('click',beforeOpen);group.append(link);
  }
  if(!group.childElementCount)return null;
  const note=document.createElement('small');note.textContent='Mở trong tab mới · cuộc trò chuyện này được giữ lại.';group.append(note);
  return group;
}
