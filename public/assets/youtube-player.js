// API chính thức, chỉ tải sau thao tác của người xem. Không gửi request lúc mở trang.
let apiPromise;
function loadAPI(){
  if(window.YT?.Player)return Promise.resolve(window.YT);
  if(apiPromise)return apiPromise;
  apiPromise=new Promise((resolve,reject)=>{
    const before=window.onYouTubeIframeAPIReady;
    const timer=setTimeout(()=>reject(Error('YouTube chưa phản hồi.')),12000);
    window.onYouTubeIframeAPIReady=()=>{clearTimeout(timer);before?.();resolve(window.YT);};
    const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';script.async=true;
    script.onerror=()=>{clearTimeout(timer);reject(Error('Chưa tải được YouTube.'));};document.head.append(script);
  }).catch(error=>{apiPromise=null;throw error;});
  return apiPromise;
}
export class YouTubePlayer {
  constructor(host,onFailure){this.host=host;this.onFailure=onFailure;this.epoch=0;}
  clear(){this.epoch++;clearTimeout(this.timer);this.player?.destroy();this.player=null;this.host.replaceChildren();this.host.hidden=true;}
  async open(video){
    this.clear();const epoch=this.epoch;
    if(!/^[A-Za-z0-9_-]{11}$/.test(video.youtube_video_id)||video.embeddable!==true){this.onFailure('Video chưa cho phép nhúng tại đây. Em có thể mở trên YouTube.');return;}
    this.host.hidden=false;
    try {
      const YT=await loadAPI();if(epoch!==this.epoch)return;
      const slot=document.createElement('div');this.host.append(slot);
      this.timer=setTimeout(()=>{if(epoch===this.epoch)this.onFailure('Trình phát chưa phản hồi. Em thử lại hoặc mở trên YouTube nhé.');},12000);
      this.player=new YT.Player(slot,{host:'https://www.youtube-nocookie.com',width:'100%',height:'100%',videoId:video.youtube_video_id,
        playerVars:{autoplay:0,playsinline:1,rel:0,origin:location.origin},
        events:{onReady:()=>{if(epoch===this.epoch)clearTimeout(this.timer);},onError:e=>{
          if(epoch!==this.epoch)return;clearTimeout(this.timer);
          this.onFailure([101,150].includes(e.data)?'Chủ video không cho phép phát nhúng. Em có thể xem trên YouTube.':e.data===100?'Video có thể đã bị xóa hoặc chuyển riêng tư. Em thử truy cập YouTube để kiểm tra.':'Video chưa phát được tại đây. Em có thể kiểm tra trên YouTube.');
        }}});
      const frame=this.host.querySelector('iframe');
      if(frame){frame.title=video.title;frame.referrerPolicy='strict-origin-when-cross-origin';}
    }catch{if(epoch===this.epoch)this.onFailure('Chưa kết nối được trình phát. Em có thể mở video trực tiếp trên YouTube.');}
  }
}
