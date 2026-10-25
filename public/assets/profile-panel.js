// Chỉ thao tác trên proposal do server trả về, không coi khảo sát là đồng ý lưu.
const labels={interests:'Sở thích',strengths:'Điểm mạnh tự nhận',growth_skills:'Kỹ năng muốn phát triển',work_preferences:'Môi trường mong muốn',careers:'Nghề chủ động quan tâm',uncertainties:'Điều còn cần làm rõ'};
let draftOwner=null;const drafts=new Map();
export function clearProfileDrafts(){draftOwner=null;drafts.clear();}
function keepDraft(key,value,version){drafts.delete(key);drafts.set(key,{value,version});while(drafts.size>120)drafts.delete(drafts.keys().next().value);}
function node(tag,text,cls){const n=document.createElement(tag);if(text)n.textContent=text;if(cls)n.className=cls;return n;}
export async function showProfile({api,session,isGuest,backendEnabled=true,profileEnabled=true,isCurrent,onRetry,onDraft,onSession,analysisFailure,ownerKey,analysisLimit=6}){
  if(draftOwner!==ownerKey){clearProfileDrafts();draftOwner=ownerKey;}
  const dialog=document.querySelector('#profile-dialog'),host=document.querySelector('#profile-content');
  host.replaceChildren(node('p','Đang mở hồ sơ…','profile-empty'));if(!dialog.open)dialog.showModal();
  if(!backendEnabled){
    const panel=node('section','','analysis-state');
    panel.append(node('h3','Giao diện mới · Phân tích chưa mở cho tài khoản này'),
      node('p','Phân tích khảo sát và lưu Hồ sơ hướng nghiệp hiện chỉ mở cho tài khoản kiểm thử được cấp quyền. Chưa có bản phân tích AI cho khảo sát này.'),
      node('p',session?.messages?.[0]?.survey?'Câu trả lời khảo sát đã được lưu cùng cuộc trò chuyện. Bạn vẫn có thể dùng chat để tìm hiểu nghề.':'Bạn vẫn có thể hoàn thành khảo sát 5 câu và trò chuyện. Không cần tự nhập Hồ sơ từ đầu.'));
    const close=node('button','Tiếp tục trò chuyện');close.type='button';close.onclick=()=>dialog.close();panel.append(close);
    host.replaceChildren(panel);return; // No protected profile/analysis calls, no fabricated proposals.
  }
  let data={enabled:false,items:[]};
  if(profileEnabled){try{data=await api('/api/ai/career-profile');}catch{if(isCurrent())host.replaceChildren(node('p','Chưa mở được hồ sơ. Đóng và mở lại để thử; dữ liệu không bị thay đổi.'));return;}}
  if(!isCurrent())return;
  host.replaceChildren();
  host.append(node('p',isGuest?'Khách: các mục bạn xác nhận chỉ lưu tạm tối đa 2 giờ. Sau đăng nhập, chọn giữ lâu dài từng mục nếu muốn.':'Chỉ các mục bạn xác nhận mới được lưu. Bạn có thể sửa hoặc xóa bất cứ lúc nào.','profile-empty'));
  if(!data.enabled)host.append(node('p','Bạn được phân tích khảo sát và trò chuyện bằng cùng AI mới. Lưu Hồ sơ đã xác nhận hiện chỉ mở cho tài khoản kiểm thử được cấp quyền; các đề xuất dưới đây chưa được lưu thành Hồ sơ riêng tư.','profile-empty'));
  const status=node('p','','profile-status');status.setAttribute('role','status');host.append(status);
  async function action(button,fn){if(button.disabled)return;button.disabled=true;status.textContent='Đang xử lý…';try{await fn();if(isCurrent())status.textContent='Đã cập nhật.';}catch{if(isCurrent()){status.textContent='Chưa lưu được hồ sơ. Những lựa chọn của bạn vẫn được giữ lại.';button.disabled=false;}}}
  const saved=node('section');saved.append(node('h3','Hồ sơ bạn đã chọn'));
  function renderSaved(){
    saved.replaceChildren(node('h3','Hồ sơ bạn đã chọn'));
    if(!data.items.length)saved.append(node('p','Chưa có mục được bạn đồng ý lưu.','profile-empty'));
    for(const item of data.items){
      const row=node('section','','profile-item');row.append(node('h4',labels[item.category]||item.category));
      const key='item:'+item.id, draft=drafts.get(key);const input=node('input');input.value=draft?.value??item.value;input.oninput=()=>keepDraft(key,input.value,draft?.version??item.version);input.maxLength=160;input.minLength=3;input.setAttribute('aria-label','Sửa '+(labels[item.category]||item.category));row.append(input);
      row.append(node('small','Đã xác nhận · cập nhật '+new Date(item.updated_at).toLocaleDateString('vi-VN')+(item.expires_at?' · đang lưu tạm':'')));
      if(item.metadata?.evidence?.length){const details=node('details');details.append(node('summary','Căn cứ của thông tin đã xác nhận'));for(const e of item.metadata.evidence)details.append(node('p',`Câu ${e.question_id}: «${e.excerpt}»`,'profile-evidence'));row.append(details);}
      const update=node('button','Lưu chỉnh sửa'),remove=node('button','Xóa mục');
      update.type=remove.type='button';
      update.onclick=()=>action(update,async()=>{if(input.value.trim().length<3)throw Error();const result=await api('/api/ai/career-profile/items/'+item.id,{method:'PATCH',body:JSON.stringify({value:input.value.trim(),version:drafts.get(key)?.version??item.version})});if(isCurrent()){drafts.delete(key);data=result;renderSaved();}});
      remove.onclick=()=>action(remove,async()=>{await api('/api/ai/career-profile/items/'+item.id,{method:'DELETE'});if(isCurrent()){drafts.delete(key);data.items=data.items.filter(p=>p.id!==item.id);renderSaved();}});
      row.append(update,remove);
      if(!isGuest&&item.expires_at){const keep=node('button','Giữ lâu dài trong tài khoản');keep.onclick=()=>action(keep,async()=>{const result=await api('/api/ai/career-profile/items/'+item.id,{method:'PATCH',body:JSON.stringify({value:input.value.trim(),version:drafts.get(key)?.version??item.version,retain:true})});if(isCurrent()){drafts.delete(key);data=result;renderSaved();}});row.append(keep);}
      saved.append(row);
    }
  }renderSaved();
  let progress={status:'pending'};
  if(session?.messages?.[0]?.survey){try{progress=await api(`/api/ai/sessions/${session.id}/analysis`);}catch{progress={status:'failed'};}}
  if(!isCurrent())return;
  const analysis=progress.result||session?.messages?.[0]?.analysis_job?.result||[...(session?.messages||[])].reverse().find(m=>m.survey_analysis)?.survey_analysis;
  const proposals=node('section');proposals.append(node('h3','Đề xuất từ khảo sát · bạn quyết định'));host.append(proposals,saved);
  if(!analysis){
    const surveyed=Boolean(session?.messages?.[0]?.survey);
    const failed=progress.status==='failed'||analysisFailure;
    const panel=node('div','',failed?'analysis-state is-error':'analysis-state');panel.setAttribute('role','status');
    panel.append(node('strong',!surveyed?'Một chút chia sẻ để bắt đầu':failed?'Chưa hoàn tất phân tích':'Đang phân tích câu trả lời của bạn...'));
    panel.append(node('p',!surveyed?'Hoàn thành 5 câu khảo sát để nhận những nhận định có căn cứ.':failed?'Bạn có thể thử lại. Câu trả lời khảo sát và những lựa chọn của bạn vẫn được giữ.':'Bạn không cần nhập lại thông tin. Hệ thống đang đối chiếu các câu trả lời để đề xuất hồ sơ.'));
    if(surveyed&&failed){const button=node('button','Thử phân tích lại');button.type='button';button.onclick=()=>{button.disabled=true;onRetry();};panel.append(button);}
    panel.append(node('small',`Tối đa ${analysisLimit} lần phân tích/ngày, gồm lần thử lại; không trừ lượt chat miễn phí.`));
    proposals.append(panel);return;
  }
  proposals.append(node('p',analysis.summary));
  for(const question of analysis.clarification_questions||[])proposals.append(node('p','Cần làm rõ: '+question));
  if(analysis.clarification_questions?.length){const clarify=node('button','Làm rõ thêm','profile-clarify');clarify.type='button';clarify.onclick=()=>{dialog.close();onDraft(analysis.clarification_questions.join('\n'));};proposals.append(clarify);}
  for(const proposal of analysis.proposed_profile_items){
    if(data.items.some(i=>i.source_proposal_id===proposal.id)||session.messages[0].profile_rejections?.includes(proposal.id))continue;
    const row=node('section','','profile-proposal');row.append(node('h4',labels[proposal.category]||proposal.category));
    const key='proposal:'+session.id+':'+proposal.id;const value=node('textarea');value.value=drafts.get(key)?.value??proposal.value;value.oninput=()=>keepDraft(key,value.value);value.maxLength=160;value.rows=2;value.setAttribute('aria-label','Xem và chỉnh nhận định');row.append(value);
    row.append(node('small',proposal.confidence,'confidence-label'));const detail=node('details');detail.append(node('summary','Vì sao có nhận định này?'));
    for(const e of proposal.evidence)detail.append(node('p',`Câu ${e.question_id}: «${e.excerpt}»`,'profile-evidence'));row.append(detail);
    const accept=node('button','Chấp nhận'),reject=node('button','Từ chối');accept.disabled=!data.enabled||proposal.proposed_action!=='confirm';
    accept.onclick=()=>action(accept,async()=>{if(value.value.trim().length<3)throw Error();const result=await api('/api/ai/career-profile/items',{method:'POST',body:JSON.stringify({session_id:session.id,proposal_id:proposal.id,value:value.value.trim(),confirmed:true})});if(isCurrent()){drafts.delete(key);data=result;row.remove();renderSaved();}});
    reject.onclick=()=>action(reject,async()=>{const result=await api(`/api/ai/sessions/${session.id}/profile-proposals/${proposal.id}/reject`,{method:'POST'});if(isCurrent()){onSession?.(result.session);row.remove();}});row.append(accept,reject);proposals.append(row);
    if(!data.enabled)reject.disabled=true;
  }
}
