// Chỉ thao tác trên proposal do server trả về, không coi khảo sát là đồng ý lưu.
const labels={interests:'Sở thích',strengths:'Điểm mạnh tự nhận',growth_skills:'Kỹ năng muốn phát triển',work_preferences:'Môi trường mong muốn',careers:'Nghề chủ động quan tâm',uncertainties:'Điều còn cần làm rõ'};
function node(tag,text,cls){const n=document.createElement(tag);if(text)n.textContent=text;if(cls)n.className=cls;return n;}
export async function showProfile({api,session,isGuest,isCurrent,onAnalyze,onDraft}){
  const dialog=document.querySelector('#profile-dialog'),host=document.querySelector('#profile-content');
  host.replaceChildren(node('p','Đang mở hồ sơ…','profile-empty'));if(!dialog.open)dialog.showModal();
  let data;
  try{data=await api('/api/ai/career-profile');}catch{if(isCurrent())host.replaceChildren(node('p','Chưa mở được hồ sơ. Đóng và mở lại để thử; dữ liệu không bị thay đổi.'));return;}
  if(!isCurrent())return;
  host.replaceChildren();
  host.append(node('p',isGuest?'Khách: các mục bạn xác nhận chỉ lưu tạm tối đa 2 giờ. Sau đăng nhập, chọn giữ lâu dài từng mục nếu muốn.':'Chỉ các mục bạn xác nhận mới được lưu. Bạn có thể sửa hoặc xóa bất cứ lúc nào.','profile-empty'));
  if(!data.enabled)host.append(node('p','Hồ sơ có xác nhận chưa bật ở môi trường này; đề xuất vẫn có thể xem nếu AI phân tích thành công.','profile-empty'));
  const status=node('p','','profile-status');status.setAttribute('role','status');host.append(status);
  async function action(button,fn){if(button.disabled)return;button.disabled=true;status.textContent='Đang xử lý…';try{await fn();if(isCurrent())status.textContent='Đã cập nhật.';}catch{if(isCurrent()){status.textContent='Chưa cập nhật được. Mở lại hồ sơ và thử lại; không tự gửi lại thao tác.';button.disabled=false;}}}
  const saved=node('section');saved.append(node('h3','Thông tin đã xác nhận'));host.append(saved);
  function renderSaved(){
    saved.replaceChildren(node('h3','Thông tin đã xác nhận'));
    if(!data.items.length)saved.append(node('p','Chưa có mục được bạn đồng ý lưu.','profile-empty'));
    for(const item of data.items){
      const row=node('section','','profile-item');row.append(node('h4',labels[item.category]||item.category));
      const input=node('input');input.value=item.value;input.maxLength=160;input.minLength=3;input.setAttribute('aria-label','Sửa '+(labels[item.category]||item.category));row.append(input);
      row.append(node('small','Đã xác nhận · cập nhật '+new Date(item.updated_at).toLocaleDateString('vi-VN')+(item.expires_at?' · đang lưu tạm':'')));
      const update=node('button','Lưu chỉnh sửa'),remove=node('button','Xóa mục');
      update.type=remove.type='button';
      update.onclick=()=>action(update,async()=>{if(input.value.trim().length<3)throw Error();const result=await api('/api/ai/career-profile/items/'+item.id,{method:'PATCH',body:JSON.stringify({value:input.value.trim(),version:item.version})});if(isCurrent()){data=result;renderSaved();}});
      remove.onclick=()=>action(remove,async()=>{await api('/api/ai/career-profile/items/'+item.id,{method:'DELETE'});if(isCurrent()){data.items=data.items.filter(p=>p.id!==item.id);renderSaved();}});
      row.append(update,remove);
      if(!isGuest&&item.expires_at){const keep=node('button','Giữ lâu dài trong tài khoản');keep.onclick=()=>action(keep,async()=>{const result=await api('/api/ai/career-profile/items/'+item.id,{method:'PATCH',body:JSON.stringify({value:input.value.trim(),version:item.version,retain:true})});if(isCurrent()){data=result;renderSaved();}});row.append(keep);}
      saved.append(row);
    }
  }renderSaved();
  const analysis=[...(session?.messages||[])].reverse().find(m=>m.survey_analysis)?.survey_analysis;
  const proposals=node('section');proposals.append(node('h3','Đề xuất từ khảo sát · bạn quyết định'));host.append(proposals);
  if(!analysis){
    proposals.append(node('p','Chưa có bản phân tích đã được kiểm tra cấu trúc. Hoàn thành khảo sát và gửi yêu cầu phân tích; mở hồ sơ không tự gọi AI.'));
    if(session?.messages?.[0]?.survey){const analyze=node('button','Phân tích khảo sát qua AI Chat (tính một lượt chat)');analyze.onclick=()=>{dialog.close();onAnalyze();};proposals.append(analyze);}return;
  }
  proposals.append(node('p',analysis.summary));
  for(const question of analysis.clarification_questions||[])proposals.append(node('p','Cần làm rõ: '+question));
  if(analysis.clarification_questions?.length){const clarify=node('button','Soạn câu hỏi để làm rõ');clarify.onclick=()=>{dialog.close();onDraft(analysis.clarification_questions.join('\n'));};proposals.append(clarify);}
  for(const proposal of analysis.proposed_profile_items){
    if(data.items.some(i=>i.source_proposal_id===proposal.id))continue;
    const row=node('section','','profile-proposal');row.append(node('h4',labels[proposal.category]||proposal.category));
    const value=node('textarea');value.value=proposal.value;value.maxLength=160;value.rows=2;value.setAttribute('aria-label','Xem và chỉnh nhận định');row.append(value);
    row.append(node('small',proposal.confidence+' · '+proposal.inference_type));
    for(const evidence of proposal.evidence)row.append(node('p',`Câu ${evidence.question_id}: «${evidence.excerpt}»`,'profile-evidence'));
    const accept=node('button','Chấp nhận và lưu mục này'),reject=node('button','Từ chối');accept.disabled=!data.enabled||proposal.proposed_action!=='confirm';
    accept.onclick=()=>action(accept,async()=>{if(value.value.trim().length<3)throw Error();const result=await api('/api/ai/career-profile/items',{method:'POST',body:JSON.stringify({session_id:session.id,proposal_id:proposal.id,value:value.value.trim(),confirmed:true})});if(isCurrent()){data=result;row.remove();renderSaved();}});
    reject.onclick=()=>row.remove();row.append(accept,reject);proposals.append(row);
  }
}
