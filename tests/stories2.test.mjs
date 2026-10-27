import test from 'node:test';
import assert from 'node:assert/strict';
const values=new Map();
globalThis.sessionStorage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v)};
const {offerStoryQuestion,offerVideoQuestion,storyQuestion}=await import('../public/assets/story-journey.js');
const story={career_id:'kiem-sat-vien',title:'Chi tiết gỡ tội không được bỏ quên'};
const scene={scene_id:'scene-2',title:'Lựa chọn',caption:'Một chi tiết trong hồ sơ cần được làm rõ.'};
test('editable question carries exact career, scene and summary, scoped to one session',()=>{
  assert.equal(offerStoryQuestion(story,scene,'Câu hỏi đã chỉnh'),true);
  assert.equal(storyQuestion('bac-si','s1'),null);
  const v=storyQuestion(story.career_id,'s1');
  assert.match(v.text,/scene-2/);assert.match(v.text,/Câu hỏi đã chỉnh/);assert.match(v.text,/Một chi tiết/);
  assert.equal(v.path,'/mot-ngay-lam-viec?nghe=kiem-sat-vien&scene=scene-2');
  assert.equal(storyQuestion(story.career_id,'other-session'),null);
});
test('expired, future, malformed and missing timestamp do not restore',()=>{
  for(const extra of [{at:0},{at:Date.now()+100000},{at:undefined},{scene_id:'../../secret'}]){
    values.set('laban.story-handoff.v2',JSON.stringify({...story,...scene,summary:'summary',scene_title:'scene',question:'question',at:Date.now(),...extra}));
    assert.equal(storyQuestion(story.career_id,'s1'),null);
  }
  values.set('laban.story-handoff.v2','broken');assert.equal(storyQuestion(story.career_id,'s1'),null);
});
test('blocked browser storage fails without an AI call',()=>{
  const original=sessionStorage.setItem;sessionStorage.setItem=()=>{throw Error('blocked');};
  assert.equal(offerStoryQuestion(story,scene,'Câu hỏi'),false);sessionStorage.setItem=original;
});

test('video draft retains verified source and returns to exact video, bound to one conversation',()=>{
  const video={career_id:'lap-trinh',youtube_video_id:'_WQ_VV4pXPc',title:'Software Developers Career Video',channel_name:'CareerOneStop',description:'Working on software.',featured_tasks:['Write code']};
  assert.equal(offerVideoQuestion(video,'Em muốn hỏi về kỹ năng'),true);
  assert.equal(storyQuestion('thiet-ke','v1'),null);
  const draft=storyQuestion('lap-trinh','v1');
  assert.match(draft.text,/https:\/\/www.youtube.com\/watch\?v=_WQ_VV4pXPc/);
  assert.match(draft.text,/Em muốn hỏi về kỹ năng/);
  assert.equal(draft.path,'/mot-ngay-lam-viec?nghe=lap-trinh&tab=video&video=_WQ_VV4pXPc');
  assert.equal(draft.label,'Quay lại video');
  assert.equal(storyQuestion('lap-trinh','other'),null);
  assert.equal(offerVideoQuestion({...video,youtube_video_id:'../../evil'},'q'),false);
  const saved=JSON.parse(values.get('laban.story-handoff.v2'));
  values.set('laban.story-handoff.v2',JSON.stringify({...saved,video_id:'../../evil'}));
  assert.equal(storyQuestion('lap-trinh','v1'),null);
});
