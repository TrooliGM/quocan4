const $ = (s) => document.querySelector(s);
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icons = {
  code: '<rect x="8" y="8" width="94" height="65" rx="7" fill="#fffdf5" stroke="#203c36" stroke-width="3"/><path d="M8 23h94M40 39l-12 9 12 9m30-18 12 9-12 9m-11-21-8 25M43 74l-4 13h33l-4-13" fill="none" stroke="#203c36" stroke-width="3" stroke-linecap="round"/><circle cx="18" cy="16" r="2" fill="#ec7357"/><circle cx="25" cy="16" r="2" fill="#ec7357"/>',
  design: '<rect x="16" y="14" width="73" height="65" rx="6" fill="#fffdf5" stroke="#203c36" stroke-width="3"/><circle cx="39" cy="34" r="9" fill="#ec7357"/><path d="M22 68l21-20 15 13 14-24 12 31" fill="#c6dfcb" stroke="#203c36" stroke-width="2"/><path d="M83 11l9 3-20 61-9 7-2-12z" fill="#f5d88b" stroke="#203c36" stroke-width="2"/>',
  health: '<rect x="18" y="19" width="76" height="64" rx="12" fill="#fffdf5" stroke="#203c36" stroke-width="3"/><path d="M42 19v-9h26v9" fill="none" stroke="#203c36" stroke-width="3"/><path d="M49 34h14v11h11v14H63v11H49V59H38V45h11z" fill="#ec7357"/>',
  book: '<path d="M55 22Q34 8 11 19v60q22-11 44 3 22-14 44-3V19Q76 8 55 22Z" fill="#fffdf5" stroke="#203c36" stroke-width="3"/><path d="M55 22v60M23 32l19 3m-19 10 19 3m-19 10 19 3m27-27 17-4m-17 17 17-4m-17 17 17-4" fill="none" stroke="#203c36" stroke-width="3" stroke-linecap="round"/>',
  leaf: '<path d="M55 79C0 66 16 18 27 11c10 26 48 17 47 43 0 11-8 22-19 25z" fill="#b4d5b9" stroke="#203c36" stroke-width="3"/><path d="M55 83c23-14 39-33 40-57-30 0-48 18-40 57z" fill="#fffdf5" stroke="#203c36" stroke-width="3"/><path d="M37 35q22 25 18 54m25-43L55 83" fill="none" stroke="#203c36" stroke-width="3"/>',
  chat: '<path d="M13 17h76a8 8 0 0 1 8 8v40a8 8 0 0 1-8 8H51L30 88V73H13a8 8 0 0 1-8-8V25a8 8 0 0 1 8-8z" fill="#fffdf5" stroke="#203c36" stroke-width="3"/><path d="M23 35h55M23 46h45M23 57h30" fill="none" stroke="#203c36" stroke-width="3" stroke-linecap="round"/><circle cx="85" cy="15" r="13" fill="#ec7357"/><path d="M79 15h12m-6-6v12" stroke="#fffdf5" stroke-width="3"/>'
};
let careerData = [], articleData = [], category = '', allCareers = false, searchController;
async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  let data;
  try { data = await response.json(); } catch { throw new Error('Chưa tải được nội dung. Bạn thử lại nhé.'); }
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Bạn nhập câu hỏi từ 3 đến 600 ký tự nhé.');
  return data;
}
function renderCareers(items) {
  const shown = allCareers || category || $('#career-search').value.trim() ? items : items.slice(0, 3);
  $('#career-status').textContent = `Tìm thấy ${items.length} nghề. Đang hiển thị ${shown.length} nghề.`;
  if (!items.length) {
    $('#career-grid').innerHTML = '<div class="col-12"><div class="empty-state"><h3>Chưa tìm thấy nghề này</h3><p>Thử một từ khóa khác hoặc khám phá tất cả nghề nhé.</p><button class="btn btn-ink" id="reset-search">Xem tất cả nghề →</button></div></div>';
    $('#reset-search').addEventListener('click', resetSearch);
    return;
  }
  $('#career-grid').innerHTML = shown.map((c, i) => `<div class="col-md-6 col-lg-4 reveal" style="animation-delay:${i * 60}ms"><article class="career-card"><div class="career-art ${escapeHTML(c.color)}"><span class="category-label">${escapeHTML(c.category)}</span><svg viewBox="0 0 110 95" aria-hidden="true">${icons[c.icon] || icons.book}</svg></div><div class="career-body"><span class="career-tag">${escapeHTML(c.tag)}</span><h3>${escapeHTML(c.name)}</h3><p>${escapeHTML(c.description)}</p><button data-career="${escapeHTML(c.id)}" aria-label="Khám phá nghề ${escapeHTML(c.name)}">Khám phá nghề <span aria-hidden="true">↗</span></button></div></article></div>`).join('');
}
async function loadCareers() {
  searchController?.abort();
  const controller = new AbortController(); searchController = controller;
  $('#career-grid').setAttribute('aria-busy', 'true');
  const params = new URLSearchParams({q: $('#career-search').value.trim(), category});
  try {
    const data = await fetchJSON(`/api/careers?${params}`, {signal: controller.signal});
    data.items.forEach((item) => { if (!careerData.some((c) => c.id === item.id)) careerData.push(item); });
    renderCareers(data.items);
  } catch (error) {
    if (error.name === 'AbortError') return;
    $('#career-grid').innerHTML = '<div class="col-12"><div class="empty-state"><p>Chưa tải được danh sách nghề.</p><button class="btn btn-ink" id="retry-careers">Thử lại</button></div></div>';
    $('#retry-careers').addEventListener('click', loadCareers);
    $('#career-status').textContent = 'Chưa tải được danh sách nghề.';
  } finally { if (searchController === controller) $('#career-grid').removeAttribute('aria-busy'); }
}
function selectCategory(value) {
  category = value;
  document.querySelectorAll('[data-category]').forEach((button) => {
    const selected = button.dataset.category === value;
    button.classList.toggle('selected', selected); button.setAttribute('aria-pressed', String(selected));
  });
}
function resetSearch() {
  $('#career-search').value = ''; allCareers = true; selectCategory(''); loadCareers();
  $('#show-all').textContent = 'Đang hiển thị tất cả nghề ↗';
}
function openContent(title, html) {
  $('#dialog-content').innerHTML = `<h2 id="dialog-title">${escapeHTML(title)}</h2>${html}`;
  $('#content-dialog').showModal();
}
function openCareer(id) {
  const c = careerData.find((item) => item.id === id);
  if (!c) return;
  openContent(c.name, `<span class="eyebrow">${escapeHTML(c.category)} · KHÁM PHÁ NGHỀ</span><p>${escapeHTML(c.description)}</p><h3>Một ngày làm việc có thể gồm</h3><ol class="day-list">${c.day.map((s) => `<li>${escapeHTML(s)}</li>`).join('')}</ol><h3>Những kỹ năng đáng rèn luyện</h3><div class="skill-tags">${c.skills.map((s) => `<span>${escapeHTML(s)}</span>`).join('')}</div><h3>Thử một bước nhỏ hôm nay</h3><p class="first-step">${escapeHTML(c.first_step)}</p><p class="content-note">Nội dung giới thiệu của bản mẫu; công việc cụ thể thay đổi theo vị trí và nơi làm việc.</p>`);
}
function renderArticles() {
  $('#article-grid').innerHTML = articleData.map((a, i) => `<div class="col-md-6 col-lg-4"><article class="article-card"><div class="article-cover ${escapeHTML(a.color)}"><span>${escapeHTML(a.category.toLocaleUpperCase('vi'))}</span><i aria-hidden="true">${['✳', '↗', '“'][i % 3]}</i><strong aria-hidden="true">${escapeHTML(a.number)}</strong></div><div class="article-body"><span class="reading-time">LA BÀN BIÊN SOẠN · ${a.minutes} PHÚT ĐỌC</span><h3>${escapeHTML(a.title)}</h3><p>${escapeHTML(a.summary)}</p><button data-article="${escapeHTML(a.id)}" aria-label="Đọc bài ${escapeHTML(a.title)}">Đọc câu chuyện ↗</button></div></article></div>`).join('');
}
async function loadArticles() {
  try { articleData = (await fetchJSON('/api/articles')).items; renderArticles(); }
  catch {
    $('#article-grid').innerHTML = '<div class="col-12"><div class="empty-state"><p>Chưa tải được bài viết.</p><button id="retry-articles" class="btn btn-ink">Thử lại</button></div></div>';
    $('#retry-articles').addEventListener('click', loadArticles);
  }
}
document.addEventListener('click', (event) => {
  const career = event.target.closest('[data-career]'); if (career) openCareer(career.dataset.career);
  const article = event.target.closest('[data-article]');
  if (article) {
    const a = articleData.find((item) => item.id === article.dataset.article);
    if (a) openContent(a.title, `<span class="eyebrow">${escapeHTML(a.category)} · ${a.minutes} PHÚT ĐỌC</span>${a.body.map((p) => `<p>${escapeHTML(p)}</p>`).join('')}`);
  }
  if (event.target.closest('[data-open-ai]')) $('#ai-dialog').showModal();
  const example = event.target.closest('[data-ai-question]');
  if (example) { $('#ai-question').value = example.dataset.aiQuestion; $('#ai-question').focus(); }
});
document.querySelectorAll('dialog').forEach((dialog) => {
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (e) => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
});
$('#search-form').addEventListener('submit', (e) => { e.preventDefault(); allCareers = true; loadCareers(); $('#careers').scrollIntoView({behavior:'smooth'}); });
let debounce;
$('#career-search').addEventListener('input', () => { clearTimeout(debounce); debounce = setTimeout(loadCareers, 250); });
document.querySelectorAll('[data-category]').forEach((b) => b.addEventListener('click', () => { selectCategory(b.dataset.category); allCareers = true; loadCareers(); }));
document.querySelectorAll('[data-query]').forEach((b) => b.addEventListener('click', () => { selectCategory(''); $('#career-search').value = b.dataset.query; $('#search-form').requestSubmit(); }));
$('#show-all').addEventListener('click', resetSearch);
$('#menu-toggle').addEventListener('click', () => { const open = $('#nav-links').classList.toggle('open'); $('#menu-toggle').setAttribute('aria-expanded', String(open)); });
document.querySelectorAll('#nav-links a').forEach((link) => link.addEventListener('click', () => { $('#nav-links').classList.remove('open'); $('#menu-toggle').setAttribute('aria-expanded', 'false'); }));
$('#ai-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = $('#ai-question').value.trim();
  const answer = $('#ai-answer');
  if (question.length < 3) { answer.textContent = 'Bạn nhập câu hỏi ít nhất 3 ký tự nhé.'; return; }
  $('#ai-submit').disabled = true; $('#ai-submit').textContent = 'Đang suy nghĩ…'; answer.classList.remove('error'); answer.textContent = 'La Bàn đang tìm một gợi ý cho bạn…';
  try {
    const result = await fetchJSON('/api/advice', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({question}), signal:AbortSignal.timeout(35000)});
    answer.textContent = result.answer;
  } catch (error) { answer.classList.add('error'); answer.textContent = error.name === 'TimeoutError' ? 'Phản hồi hơi lâu. Bạn thử lại sau nhé.' : error.message; }
  finally { $('#ai-submit').disabled = false; $('#ai-submit').textContent = 'Gửi câu hỏi ↗'; }
});
async function initialize() {
  await Promise.allSettled([
    (async () => { try { careerData = (await fetchJSON('/api/careers')).items; renderCareers(careerData); } catch { await loadCareers(); } })(),
    loadArticles()
  ]);
}
initialize();
