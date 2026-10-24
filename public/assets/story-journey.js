// Chỉ dữ liệu học trong tab, không phải bằng chứng xác thực hay kết luận về người dùng.
const KEY='laban.story-handoff.v2', TTL=2*60*60*1000;
export function offerStoryQuestion(story, scene, question) {
  const value={career_id:story.career_id,scene_id:scene.scene_id,title:story.title,
    scene_title:scene.title,summary:scene.caption.slice(0,600),question:question.slice(0,600),at:Date.now()};
  try { sessionStorage.setItem(KEY,JSON.stringify(value));return true; } catch {return false;}
}
export function offerVideoQuestion(video,question){
  if(!/^[A-Za-z0-9_-]{11}$/.test(video.youtube_video_id))return false;
  const value={type:'video',career_id:video.career_id,video_id:video.youtube_video_id,title:video.title.slice(0,600),
    scene_title:video.channel_name.slice(0,600),summary:(video.description+' '+video.featured_tasks.join('; ')).slice(0,600),question:question.slice(0,600),at:Date.now()};
  try{sessionStorage.setItem(KEY,JSON.stringify(value));return true;}catch{return false;}
}
export function storyQuestion(career, session) {
  try {
    const v=JSON.parse(sessionStorage.getItem(KEY));
    if (!v || !Number.isFinite(v.at) || Date.now()<v.at || Date.now()-v.at>TTL || v.career_id!==career || (v.type==='video'?!/^[A-Za-z0-9_-]{11}$/.test(v.video_id):!/^scene-[1-6]$/.test(v.scene_id)) || (v.session && v.session!==session)) return null;
    if (['title','scene_title','summary','question'].some(k=>typeof v[k]!=='string'||v[k].length>600)) return null;
    v.session=session;sessionStorage.setItem(KEY,JSON.stringify(v));
    if(v.type==='video')return {text:`Em đang tìm hiểu nghề qua video YouTube “${v.title}”, kênh ${v.scene_title}. Nguồn: https://www.youtube.com/watch?v=${v.video_id}. Tóm tắt biên tập: ${v.summary}\n\n${v.question}\nHãy phân tích nhiệm vụ và kỹ năng dựa trên ngữ cảnh đã cung cấp; không tự nói đã xem video hoặc suy năng lực của em.`,
      path:'/mot-ngay-lam-viec?nghe='+encodeURIComponent(career)+'&tab=video&video='+v.video_id,label:'Quay lại video'};
    return {text:`Em đang đọc truyện “${v.title}”, cảnh ${v.scene_id}: ${v.scene_title}. Tình huống: ${v.summary}\n\n${v.question}\nHãy giải thích kỹ năng, trách nhiệm và các hướng tiếp cận; không suy đoán năng lực của em từ lựa chọn trong truyện.`,
      path:'/mot-ngay-lam-viec?nghe='+encodeURIComponent(career)+'&scene='+v.scene_id};
  } catch { return null; }
}
