const $ = (s) => document.querySelector(s);
let pendingAdvice;
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  let data;
  try { data = await response.json(); } catch { throw new Error('Chưa tải được nội dung. Bạn thử lại nhé.'); }
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : data.detail?.message || 'Chưa thực hiện được. Bạn thử lại nhé.');
  return data;
}
function openCareer(id) { window.openLibraryCareer?.(id); }

document.addEventListener('click', (event) => {
  const career = event.target.closest('[data-career]'); if (career) openCareer(career.dataset.career);
  if (event.target.closest('[data-open-ai]')) $('#ai-dialog').showModal();
  const example = event.target.closest('[data-ai-question]');
  if (example) { $('#ai-question').value = example.dataset.aiQuestion; $('#ai-question').focus(); }
});
document.querySelectorAll('dialog').forEach((dialog) => {
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (e) => { if (e.target === dialog) { const r = dialog.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) dialog.close(); } });
});
$('#ai-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = $('#ai-question').value.trim();
  const answer = $('#ai-answer');
  if (question.length < 3) { answer.textContent = 'Bạn nhập câu hỏi ít nhất 3 ký tự nhé.'; return; }
  $('#ai-submit').disabled = true; $('#ai-submit').textContent = 'Đang suy nghĩ…'; answer.classList.remove('error'); answer.textContent = 'La Bàn đang tìm một gợi ý cho bạn…';
  try {
    if (pendingAdvice?.question !== question) pendingAdvice = {question,request_id:crypto.randomUUID()};
    const {aiHeaders} = await import('./ai-access.js');
    const result = await fetchJSON('/api/advice', {method:'POST', headers:await aiHeaders(), body:JSON.stringify(pendingAdvice), signal:AbortSignal.timeout(35000)});
    answer.textContent = result.answer;
    pendingAdvice = null;
  } catch (error) { answer.classList.add('error'); answer.textContent = error.name === 'TimeoutError' ? 'Phản hồi hơi lâu. Bạn thử lại sau nhé.' : error.message; }
  finally { $('#ai-submit').disabled = false; $('#ai-submit').textContent = 'Gửi câu hỏi ↗'; }
});
