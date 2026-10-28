import {navigationButtons} from './navigation-actions.js?v=task44-2';

// Chỉ dựng dữ liệu đã lưu, không fetch/gọi AI/ghi tin nhắn hoặc xác nhận Hồ sơ.
export function surveyResult({result,job,busy,error,onRetry,beforeOpen}) {
  const row=document.createElement('article');row.className='message-row assistant survey-analysis-result';
  const bubble=document.createElement('div');bubble.className='message-bubble survey-result';row.append(bubble);
  const heading=document.createElement('h2');heading.textContent='Cùng nhìn lại những điều bạn chia sẻ';bubble.append(heading);
  const p=text=>{const node=document.createElement('p');node.textContent=text;bubble.append(node);};
  if(!result){
    const interrupted=job?.status==='processing' && job.lease_until*1000<=Date.now();
    p(busy?'Đang phân tích 5 câu trả lời của bạn…':error|| (job?.status==='failed'||interrupted?'Chưa thể phân tích khảo sát. Câu trả lời của bạn vẫn được giữ nguyên.':'Khảo sát đã được lưu. Bạn có thể tiếp tục trò chuyện hoặc phân tích khi sẵn sàng.'));
    if(!busy){const retry=document.createElement('button');retry.type='button';retry.className='analysis-retry';retry.textContent='Thử phân tích khảo sát';retry.addEventListener('click',onRetry);bubble.append(retry);}
    return row;
  }
  p(result.summary||'');
  const list=(parent,values)=>{const ul=document.createElement('ul');for(const value of (values||[]).slice(0,16)){const li=document.createElement('li');li.textContent=value;ul.append(li);}if(ul.childElementCount)parent.append(ul);};
  const facts=Array.isArray(result.proposed_profile_items)?result.proposed_profile_items:[];
  if(facts.length){const details=document.createElement('details'),title=document.createElement('summary');title.textContent='Căn cứ từ câu trả lời của bạn';details.append(title);
    for(const item of facts.slice(0,16)){const line=document.createElement('p');line.textContent=item.value;for(const e of item.evidence||[]){const small=document.createElement('small');small.textContent=`Câu ${e.question_id}: “${e.excerpt}”`;line.append(small);}details.append(line);}bubble.append(details);}
  const directions=Array.isArray(result.career_directions)?result.career_directions:[];
  if(directions.length){const title=document.createElement('h3');title.textContent='Những hướng nghề đáng khám phá';bubble.append(title);}
  for(const direction of directions.slice(0,3)){
    const card=document.createElement('section');card.className='survey-direction';const title=document.createElement('h4');title.textContent=direction.career_name;card.append(title);
    const reason=document.createElement('p');reason.textContent=direction.reason;card.append(reason);
    for(const [key,label] of [['subjects','Môn học liên quan'],['skills','Kỹ năng có thể rèn'],['activities','Trải nghiệm nhỏ, an toàn']]){const strong=document.createElement('strong');strong.textContent=label;card.append(strong);list(card,direction[key]);}
    const buttons=navigationButtons([{kind:'career_profile',career_id:direction.career_id,label:'Xem hồ sơ · '+direction.career_name,href:'/?career='+direction.career_id+'#careers'}],beforeOpen);if(buttons)card.append(buttons);bubble.append(card);
  }
  if(result.clarification_questions?.length){const title=document.createElement('h3');title.textContent='Mình cùng tìm hiểu thêm';bubble.append(title);list(bubble,result.clarification_questions);}
  const note=document.createElement('small');note.textContent='Đây là gợi ý để khám phá, chưa phải kết luận về năng lực hay mức độ phù hợp. Bạn có thể hỏi tiếp ngay bên dưới.';bubble.append(note);
  return row;
}
