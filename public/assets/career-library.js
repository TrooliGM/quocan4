const $ = s => document.querySelector(s);
const escape = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let categories=[], category='', offset=0, generation=0, modalGeneration=0, selected=false;
const symbols=['⌘','✚','▤','⚙','◇','▥','✳','◉','⚖','♧','☀','⚗'];
async function json(url) {
  const response=await fetch(url); const body=await response.json();
  if(!response.ok) throw new Error(typeof body.detail==='string'?body.detail:'Chưa tải được dữ liệu.');
  return body;
}
function categoryState(){
  document.querySelectorAll('[data-field]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.field===category)));
  $('#library-reset').hidden=!selected;
}
async function load(append=false){
  const ticket=++generation;
  if(!append){offset=0;$('#career-grid').replaceChildren();}
  $('#library-more').hidden=true;$('#career-status').textContent='Đang tìm nghề…';
  try{
    const params=new URLSearchParams({q:$('#career-search').value.trim(),category_id:category,offset:String(offset),limit:'12'});
    const data=await json('/api/career-library?'+params);
    if(ticket!==generation)return;
    for(const c of data.items){
      const button=document.createElement('button');button.className='library-card';
      button.innerHTML=`<span class="library-tag">${escape(categories.find(x=>x.category_id===c.category_id)?.name||'')}</span><h3>${escape(c.name)}</h3><p>${escape(c.short_description)}</p><span class="library-card-link">Tìm hiểu nghề <span aria-hidden="true">↗</span></span>`;
      button.addEventListener('click',()=>openCareer(c.career_id));$('#career-grid').append(button);
    }
    offset+=data.items.length;
    $('#career-status').textContent=data.total?`${data.total} nghề · Đang xem ${offset} nghề`:'Chưa tìm thấy nghề. Em thử từ khóa khác hoặc bỏ bộ lọc nhé.';
    $('#library-more').hidden=offset>=data.total;
  }catch(error){if(ticket===generation)$('#career-status').textContent=error.message+' Em có thể bấm Tìm kiếm để thử lại.';}
}
async function openCareer(id){
  const ticket=++modalGeneration;
  const dialog=$('#content-dialog'), content=$('#dialog-content');
  content.innerHTML='<h2 id="dialog-title">Đang mở nghề…</h2>';
  if(!dialog.open)dialog.showModal();
  try{
    const c=await json('/api/career-library/'+encodeURIComponent(id));
    if(ticket!==modalGeneration||!dialog.open)return;
    const lists=(title,items)=>`<h3>${title}</h3><ul>${items.map(x=>`<li>${escape(x)}</li>`).join('')}</ul>`;
    content.innerHTML=`<span class="eyebrow">${escape(categories.find(x=>x.category_id===c.category_id)?.name||'KHÁM PHÁ NGHỀ')}</span><h2 id="dialog-title">${escape(c.name)}</h2><p>${escape(c.description)}</p>${lists('Công việc thường ngày',c.daily_tasks)}${lists('Kỹ năng hữu ích',c.skills)}${lists('Môn học liên quan',c.related_subjects)}<h3>Môi trường làm việc</h3><p>${escape(c.work_environment)}</p>${lists('Khó khăn và thử thách',c.challenges)}<div class="library-modal-actions"><a class="btn btn-coral" href="/ai-career-advisor?mode=career_exploration&amp;career_id=${encodeURIComponent(c.career_id)}">Cùng tìm hiểu nghề ↗</a><a class="btn btn-ink" href="/mot-ngay-lam-viec?nghe=${encodeURIComponent(c.career_id)}">Xem truyện một ngày làm việc →</a></div><p class="content-note">Điều kiện đào tạo và hành nghề cần kiểm tra tại cơ sở đào tạo hoặc cơ quan chuyên môn. Bản mô tả không thay thế tư vấn chuyên môn.</p>`;
  }catch(e){if(ticket!==modalGeneration||!dialog.open)return;content.replaceChildren();const title=document.createElement('h2');title.id='dialog-title';title.textContent=e.message;content.append(title);}
}
window.openLibraryCareer=openCareer;
$('#search-form').addEventListener('submit',event=>{event.preventDefault();selected=true;categoryState();load();});
let debounce;$('#career-search').addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(()=>{if($('#career-search').value.trim()){selected=true;categoryState();load();}else reset();},250);});
$('#show-all').addEventListener('click',()=>{selected=true;category='';$('#career-search').value='';categoryState();load();});
$('#library-more').addEventListener('click',()=>load(true));
function reset(){generation++;selected=false;category='';offset=0;$('#career-search').value='';$('#career-grid').replaceChildren();$('#library-more').hidden=true;$('#career-status').textContent='Chọn lĩnh vực hoặc tìm kiếm để bắt đầu.';categoryState();}
$('#library-reset').addEventListener('click',reset);
try{
  categories=(await json('/api/career-library/categories')).items;
  categories.forEach((c,i)=>{const button=document.createElement('button');button.dataset.field=c.category_id;button.setAttribute('aria-pressed','false');button.innerHTML=`<span class="field-symbol" aria-hidden="true">${symbols[i]}</span><strong>${escape(c.name)}</strong><small>${c.count} nghề <span aria-hidden="true">↗</span></small>`;button.addEventListener('click',()=>{category=c.category_id;selected=true;$('#career-search').value='';categoryState();load();});$('#library-categories').append(button);});reset();
}catch(e){$('#career-status').textContent=e.message;}
