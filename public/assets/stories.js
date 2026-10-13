import {storyArt} from './story-art.js';
const $ = s => document.querySelector(s);
const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let story, index = 0, mode = 'play', playing = false, timer, request, askRequest, requestedId;
let answers = new Map();
async function json(url, options={}) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw new Error(typeof body.detail === 'string' ? body.detail : 'Chưa tải được nội dung. Bạn thử lại nhé.');
  return body;
}
function pause() {
  playing=false; clearTimeout(timer); timer=null;
  $('#play-toggle').textContent='▶ Tự chuyển cảnh'; $('#play-toggle').setAttribute('aria-pressed','false');
}
function schedule() {
  clearTimeout(timer);
  if (!playing) return;
  timer=setTimeout(()=>{
    if (index < story.scenes.length-1) {index++;renderScene();schedule();}
    else {pause();showSummary(false);}
  }, Number($('#scene-speed').value));
}
function cancelAsk() {
  askRequest?.abort();askRequest=null;
  $('#story-ask-submit').disabled=false;$('#story-ask-submit').textContent='Hỏi La Bàn ↗';
  $('#story-answer').hidden=true;$('#story-answer').textContent='';$('#story-answer').classList.remove('error');
}
function chooseScene(next) {
  pause();index=Math.max(0,Math.min(next,story.scenes.length-1));renderScene();
}
function renderScene() {
  cancelAsk();
  const s=story.scenes[index];
  $('#scene-art').innerHTML=storyArt(s.art);
  $('#scene-time').textContent=s.time;$('#frame-number').textContent=`KHUNG ${String(index+1).padStart(2,'0')}`;
  $('#scene-kicker').textContent=`CẢNH ${index+1} · MỘT NGÀY CÙNG ${story.character.toLocaleUpperCase('vi')}`;
  $('#scene-title').textContent=s.title;$('#scene-caption').textContent=s.caption;$('#scene-speech').textContent=s.speech;
  $('#scene-skill').textContent=s.skill;$('#character-name').textContent=story.character;
  $('#scene-counter').textContent=`Cảnh ${index+1} / ${story.scenes.length}`;
  $('#prev-scene').disabled=index===0;
  $('#next-scene').textContent=index===story.scenes.length-1?'✓':'→';
  $('#next-scene').setAttribute('aria-label',index===story.scenes.length-1?'Xem tổng kết ngày':'Cảnh tiếp theo');
  $('#scene-timeline').innerHTML=story.scenes.map((panel,i)=>`<button data-scene="${i}" ${i===index?'aria-current="step"':''}><small>${escape(panel.time)}</small><strong>${escape(panel.title)}</strong></button>`).join('');
  $('#decision-question').textContent=s.question;
  $('#decision-choices').innerHTML=s.choices.map((choice,i)=>`<button data-choice="${i}" aria-pressed="false"><span>${String.fromCharCode(65+i)}</span>${escape(choice)}</button>`).join('');
  $('#decision-feedback').hidden=true;
  if(answers.has(index)) selectAnswer(answers.get(index),false);
}
function selectAnswer(choice, stop=true) {
  if(stop) pause();
  const s=story.scenes[index];answers.set(index,choice);
  document.querySelectorAll('[data-choice]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.choice)===choice)));
  $('#decision-feedback').textContent=s.feedback[choice];$('#decision-feedback').hidden=false;
}
function showSummary(focus=true) {
  pause();$('#day-summary').hidden=false;
  if(focus){$('#day-summary').focus({preventScroll:true});$('#day-summary').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});}
}
function setMode(value) {
  pause();mode=value;
  $('#player').hidden=mode!=='play';$('#comic-grid').hidden=mode!=='comic';$('#explore-scene').hidden=mode==='comic';
  ['play','comic'].forEach(m=>{$(`#mode-${m}`).setAttribute('aria-pressed',String(mode===m));$(`#mode-${m}`).classList.toggle('selected',mode===m);});
  if(mode==='comic') cancelAsk();
}
async function loadStory(id, push=true) {
  pause();cancelAsk();request?.abort();
  const current=new AbortController();request=current;requestedId=id;
  $('#story-content').hidden=true;$('#story-error').hidden=true;$('#story-loading').hidden=false;
  $('#career-shelf').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.careerId===id)));
  try {
    const data=await json(`/api/career-stories/${encodeURIComponent(id)}`,{signal:current.signal});
    if(request!==current)return;
    story=data;index=0;answers=new Map();
    if(push){const url=new URL(location.href);url.searchParams.set('nghe',id);history.pushState({},'',url);}
    document.title=`Một ngày làm ${story.name.toLocaleLowerCase('vi')} · La Bàn`;
    $('#story-category').textContent=`${story.category.toLocaleUpperCase('vi')} · ${story.scenes.length} CẢNH KHÁM PHÁ`;
    $('#career-title').textContent=`Một ngày làm ${story.name.toLocaleLowerCase('vi')}`;$('#career-intro').textContent=story.intro;
    $('#comic-grid').innerHTML=story.scenes.map((s,i)=>`<article class="comic-panel"><div class="comic-art">${storyArt(s.art)}<p class="speech-balloon">${escape(s.speech)}</p></div><div class="comic-panel-content"><span class="eyebrow">${escape(s.time)} · KHUNG ${i+1}</span><h3>${escape(s.title)}</h3><p>${escape(s.caption)}</p><button data-open-scene="${i}">Thử tình huống trong cảnh này ↗</button></div></article>`).join('');
    $('#summary-character').textContent=story.character;$('#summary-text').textContent=story.takeaway;$('#summary-step').textContent=story.first_step;
    $('#summary-skills').innerHTML=story.skills.map(s=>`<span>${escape(s)}</span>`).join('');
    $('#story-note').textContent=story.note;$('#story-source-link').href=story.source_url;$('#story-source-link').textContent=story.source_label;
    $('#day-summary').hidden=true;
    $('#story-question').value='';renderScene();setMode(mode);$('#story-content').hidden=false;
  } catch(error) {
    if(error.name==='AbortError')return;
    $('#story-error-text').textContent=error.message||'Chưa tải được truyện. Bạn thử lại nhé.';$('#story-error').hidden=false;
  } finally {if(request===current)$('#story-loading').hidden=true;}
}
$('#prev-scene').addEventListener('click',()=>chooseScene(index-1));
$('#next-scene').addEventListener('click',()=>index===story.scenes.length-1?showSummary():chooseScene(index+1));
$('#play-toggle').addEventListener('click',()=>{
  if(playing){pause();return;}
  if(index===story.scenes.length-1){index=0;renderScene();}
  playing=true;$('#play-toggle').textContent='Ⅱ Tạm dừng';$('#play-toggle').setAttribute('aria-pressed','true');schedule();
});
$('#scene-speed').addEventListener('change',schedule);
$('#mode-play').addEventListener('click',()=>setMode('play'));$('#mode-comic').addEventListener('click',()=>setMode('comic'));
$('#finish-story').addEventListener('click',()=>showSummary());
$('#restart-story').addEventListener('click',()=>{setMode('play');chooseScene(0);$('#day-summary').hidden=true;$('#player').focus({preventScroll:true});$('#player').scrollIntoView({block:'start'});});
$('#retry-story').addEventListener('click',()=>requestedId?loadStory(requestedId,false):initialize());
document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
window.addEventListener('pagehide',()=>{pause();request?.abort();askRequest?.abort();});
window.addEventListener('popstate',()=>loadStory(new URLSearchParams(location.search).get('nghe')||'bac-si',false));
$('#player').addEventListener('keydown',e=>{if(e.target!==$('#player'))return;if(e.key==='ArrowRight'){e.preventDefault();chooseScene(index+1);}if(e.key==='ArrowLeft'){e.preventDefault();chooseScene(index-1);}});
document.addEventListener('click',e=>{
  const career=e.target.closest('[data-career-id]');if(career)loadStory(career.dataset.careerId);
  const scene=e.target.closest('[data-scene]');if(scene)chooseScene(Number(scene.dataset.scene));
  const choice=e.target.closest('[data-choice]');if(choice)selectAnswer(Number(choice.dataset.choice));
  const panel=e.target.closest('[data-open-scene]');if(panel){setMode('play');chooseScene(Number(panel.dataset.openScene));$('#player').scrollIntoView({block:'start'});$('#player').focus({preventScroll:true});}
});
$('#story-question').addEventListener('focus',pause);
$('#story-ask-form').addEventListener('submit',async e=>{
  e.preventDefault();pause();cancelAsk();
  const question=$('#story-question').value.trim();if(question.length<3){$('#story-question').focus();return;}
  const current=new AbortController();askRequest=current;const timeout=setTimeout(()=>current.abort(),35000);
  $('#story-ask-submit').disabled=true;$('#story-ask-submit').textContent='Đang suy nghĩ…';
  $('#story-answer').hidden=false;$('#story-answer').textContent='La Bàn đang tìm lời giải thích…';
  try {
    const result=await json(`/api/career-stories/${encodeURIComponent(story.id)}/ask`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question,scene_index:index}),signal:current.signal});
    if(askRequest===current)$('#story-answer').textContent=result.answer;
  } catch(error) {if(askRequest===current){$('#story-answer').classList.add('error');$('#story-answer').textContent=error.name==='AbortError'?'Phản hồi hơi lâu. Bạn thử gửi lại nhé.':error.message;}}
  finally {clearTimeout(timeout);if(askRequest===current){$('#story-ask-submit').disabled=false;$('#story-ask-submit').textContent='Hỏi La Bàn ↗';askRequest=null;}}
});
async function initialize(){
  try {
    const {items}=await json('/api/career-stories');
    $('#career-shelf').innerHTML=items.map((c,i)=>`<button data-career-id="${escape(c.id)}" aria-pressed="false"><b>${String(i+1).padStart(2,'0')}</b>${escape(c.name)}</button>`).join('');
    await loadStory(new URLSearchParams(location.search).get('nghe')||'bac-si',false);
  } catch {$('#story-loading').hidden=true;$('#story-error').hidden=false;$('#story-error-text').textContent='Chưa tải được thư viện truyện. Kiểm tra kết nối rồi thử lại nhé.';}
}
initialize();
