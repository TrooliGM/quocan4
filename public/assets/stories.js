import {storyArt} from './story-art.js';
import {offerStoryQuestion} from './story-journey.js';
const $=s=>document.querySelector(s);
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let story, index=0, mode='play', answers=new Map(), controller, requestedId, catalog=[];
const TTL=24*60*60*1000;
function store() {
  if(!story)return;
  try {sessionStorage.setItem('laban.story.'+story.id,JSON.stringify({at:Date.now(),version:story.version,index,answers:[...answers]}));}catch{}
}
function restore(data) {
  try {
    const v=JSON.parse(sessionStorage.getItem('laban.story.'+data.id));
    if(!v||v.version!==data.version||Date.now()<v.at||Date.now()-v.at>TTL)return;
    if(Number.isInteger(v.index)&&v.index>=0&&v.index<data.scenes.length)index=v.index;
    if(Array.isArray(v.answers))for(const pair of v.answers) {
      if(!Array.isArray(pair)||pair.length!==2)continue;
      const [id,choice]=pair,s=data.scenes.find(s=>s.scene_id===id);
      if(s?.choices.some(c=>c.choice_id===choice))answers.set(id,choice);
    }
  }catch{}
}
async function json(url,signal) {
  const r=await fetch(url,{signal});const body=await r.json();
  if(!r.ok)throw Error(typeof body.detail==='string'?body.detail:'Chưa tải được truyện. Em thử lại nhé.');
  return body;
}
function selected(s) {return s.choices.find(c=>c.choice_id===answers.get(s.scene_id));}
function summary(focus=true) {
  $('#day-summary').hidden=false;
  $('#summary-decisions').innerHTML=story.scenes.filter(s=>s.choices.length).map(s=>{
    const c=selected(s);return `<li><strong>${esc(s.title)}:</strong> ${c?esc(c.text)+' — '+esc(c.consequence):'Em chưa chọn. Có thể quay lại thử cả hai hướng.'}</li>`;
  }).join('');
  if(focus){$('#day-summary').focus({preventScroll:true});$('#day-summary').scrollIntoView({block:'start',behavior:'instant'});}
}
function render() {
  if(!story)return;
  const s=story.scenes[index], choice=selected(s), previous=index>0?selected(story.scenes[index-1]):null;
  $('#scene-art').innerHTML=storyArt(s.art);
  $('#scene-time').textContent=s.time;$('#frame-number').textContent=`KHUNG ${String(index+1).padStart(2,'0')}`;
  $('#scene-kicker').textContent=`CẢNH ${index+1} · CÙNG ${story.character.toLocaleUpperCase('vi')}`;
  $('#scene-title').textContent=s.title;$('#scene-caption').textContent=s.caption;$('#scene-speech').textContent=s.speech;
  $('#scene-skill').textContent=s.skill;$('#scene-skill-reason').textContent=s.skill_reason;$('#character-name').textContent=story.character;
  $('#scene-consequence').hidden=!previous;$('#scene-consequence').textContent=previous?'Từ lựa chọn trước: '+previous.consequence:'';
  $('#scene-counter').textContent=`Cảnh ${index+1} / ${story.scenes.length}`;
  $('#reading-progress').max=story.scenes.length;$('#reading-progress').value=index+1;
  $('#prev-scene').disabled=index===0;$('#next-scene').textContent=index===story.scenes.length-1?'✓':'→';
  $('#next-scene').setAttribute('aria-label',index===story.scenes.length-1?'Xem tổng kết ngày':'Cảnh tiếp theo');
  $('#scene-timeline').innerHTML=story.scenes.map((p,i)=>`<button data-scene="${i}" ${index===i?'aria-current="step"':''}><small>${esc(p.time)}</small><strong>${esc(p.title)}</strong></button>`).join('');
  $('#decision-question').textContent=s.question||'Em nhận thấy điều gì trong công việc ở cảnh này?';
  $('#decision-choices').innerHTML=s.choices.map(c=>`<button data-choice="${esc(c.choice_id)}" aria-pressed="${choice===c}">${esc(c.text)}</button>`).join('');
  $('#decision-feedback').hidden=!choice;$('#decision-feedback').textContent=choice?choice.feedback+' '+choice.consequence:'';
  $('#story-question').value=story.ai_questions[0].slice(0,600);
  $('#story-answer').hidden=true;store();
}
function go(i) {if(story&&Number.isInteger(i)){index=Math.max(0,Math.min(i,story.scenes.length-1));render();}}
function view(value) {
  mode=value;$('#player').hidden=mode!=='play';$('#comic-grid').hidden=mode!=='comic';$('#explore-scene').hidden=mode==='comic';
  for(const m of ['play','comic']){$('#mode-'+m).setAttribute('aria-pressed',String(mode===m));$('#mode-'+m).classList.toggle('selected',mode===m);}
}
function shelf() {
  const norm=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/đ/g,'d').toLowerCase();
  const q=norm($('#story-search').value),category=$('#story-category-filter').value;
  const matches=catalog.filter(c=>(!category||c.category_id===category)&&norm(c.name).includes(q));
  $('#career-shelf').innerHTML=matches.slice(0,24).map(c=>`<button data-career-id="${esc(c.id)}" aria-pressed="${c.id===story?.id}">${esc(c.name)}</button>`).join('');
  $('#story-count').textContent=matches.length?`${matches.length} truyện phù hợp · Hiển thị tối đa 24, tìm theo tên để mở đúng nghề.`:'Chưa có kết quả. Em thử từ khóa khác nhé.';
}
async function loadStory(id,{push=false,resume=false,scene=null}={}) {
  store();controller?.abort();const current=new AbortController();controller=current;requestedId=id;
  if(push){const url=new URL(location.href);url.search='';url.searchParams.set('nghe',id);history.pushState({},'',url);}
  $('#story-content').hidden=true;$('#story-error').hidden=true;$('#story-loading').hidden=false;
  try {
    const data=await json('/api/career-stories/'+encodeURIComponent(id),current.signal);
    if(controller!==current)return;
    story=data;index=0;answers=new Map();
    if(resume)restore(data);
    if(scene){const i=data.scenes.findIndex(s=>s.scene_id===scene);if(i>=0)index=i;}
    document.title=data.title+' · La Bàn';
    $('#career-title').textContent=data.title;$('#career-intro').textContent=data.intro;
    $('#story-category').textContent=data.name+' · '+data.scenes.length+' CẢNH';
    $('#story-person-name').textContent=data.character;$('#story-workplace').textContent=data.workplace;
    $('#back-career').href='/?career='+encodeURIComponent(id)+'#careers';
    $('#comic-grid').innerHTML=data.scenes.map((s,i)=>`<article class="comic-panel"><div class="comic-art">${storyArt(s.art)}</div><div class="comic-panel-content"><span class="eyebrow">${esc(s.time)} · CẢNH ${i+1}</span><h3>${esc(s.title)}</h3><p>${esc(s.caption)}</p><button data-open-scene="${i}">Đọc và thử lựa chọn ↗</button></div></article>`).join('');
    $('#summary-character').textContent=data.character;$('#summary-text').textContent=data.takeaway;$('#summary-step').textContent=data.first_step;
    $('#summary-skills').innerHTML=data.skills.map(s=>`<span>${esc(s)}</span>`).join('');
    $('#summary-reflection').innerHTML=data.reflection.map(s=>`<li>${esc(s)}</li>`).join('');
    $('#story-note').textContent=data.note;$('#story-source-link').hidden=true;
    $('#story-sources').innerHTML=data.sources.filter(s=>/^https:\/\//.test(s.url)).map(s=>`<li><a href="${esc(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.label)}</a></li>`).join('');
    $('#day-summary').hidden=true;render();view(mode);shelf();$('#story-content').hidden=false;
  }catch(error){
    if(error.name==='AbortError'||controller!==current)return;
    $('#story-error-text').textContent=error.message||'Chưa tải được truyện. Em thử lại nhé.';$('#story-error').hidden=false;
  }finally{if(controller===current)$('#story-loading').hidden=true;}
}
$('#prev-scene').addEventListener('click',()=>go(index-1));
$('#next-scene').addEventListener('click',()=>index===story?.scenes.length-1?summary():go(index+1));
$('#mode-play').addEventListener('click',()=>view('play'));$('#mode-comic').addEventListener('click',()=>view('comic'));
$('#finish-story').addEventListener('click',()=>summary());
$('#restart-story').addEventListener('click',()=>{answers=new Map();$('#day-summary').hidden=true;view('play');go(0);$('#player').focus();});
$('#retry-story').addEventListener('click',()=>catalog.length?loadStory(requestedId):initialize());
$('#story-search').addEventListener('input',shelf);$('#story-category-filter').addEventListener('change',shelf);
document.addEventListener('click',e=>{
  const career=e.target.closest('[data-career-id]');if(career){loadStory(career.dataset.careerId,{push:true});return;}
  const scene=e.target.closest('[data-scene], [data-open-scene]');if(scene){view('play');go(Number(scene.dataset.scene??scene.dataset.openScene));return;}
  const button=e.target.closest('[data-choice]');if(button&&story){
    const s=story.scenes[index];if(!s.choices.some(c=>c.choice_id===button.dataset.choice))return;
    answers.set(s.scene_id,button.dataset.choice);render();
  }
});
$('#player').addEventListener('keydown',e=>{
  if(e.target!==$('#player'))return;
  if(e.key==='ArrowRight'){e.preventDefault();go(index+1);}if(e.key==='ArrowLeft'){e.preventDefault();go(index-1);}
});
$('#story-ask-form').addEventListener('submit',e=>{
  e.preventDefault();if(!story)return;
  const s=story.scenes[index],question=$('#story-question').value.trim();if(question.length<3)return;store();
  if(!offerStoryQuestion(story,s,question)){
    $('#story-answer').hidden=false;$('#story-answer').textContent='Trình duyệt đang chặn lưu trong tab. Em sao chép câu hỏi rồi mở AI Chat để gửi nhé.';return;
  }
  location.assign('/ai-career-advisor?mode=career_exploration&career_id='+encodeURIComponent(story.id));
});
window.addEventListener('pagehide',()=>{store();controller?.abort();});
function fromURL(resume=false){const p=new URLSearchParams(location.search);return loadStory(p.get('nghe')||'bac-si',{resume:resume||p.has('scene'),scene:p.get('scene')});}
window.addEventListener('popstate',()=>fromURL(true));
async function initialize(){
  try {
    catalog=(await json('/api/career-stories')).items;
    const categories=new Map(catalog.map(c=>[c.category_id,c.category]));
    $('#story-category-filter').innerHTML='<option value="">Tất cả nhóm nghề</option>'+[...categories].map(([id,name])=>`<option value="${esc(id)}">${esc(name)}</option>`).join('');
    shelf();await fromURL(performance.getEntriesByType('navigation')[0]?.type==='back_forward');
  }catch{
    $('#story-loading').hidden=true;$('#story-error').hidden=false;$('#story-error-text').textContent='Chưa tải được thư viện truyện. Em kiểm tra kết nối rồi thử lại nhé.';
  }
}
initialize();
