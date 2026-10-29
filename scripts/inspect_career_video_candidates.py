"""Metadata công khai của ứng viên; không tự duyệt hay chạm database."""
import json,re,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import httpx
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from research_career_videos import load,save
CACHE=R/'artifacts/video-research/metadata';CACHE.mkdir(parents=True,exist_ok=True)

def inspect(key):
    file=CACHE/(key+'.json')
    if file.exists():return json.loads(file.read_text(encoding='utf8'))
    try:
        with httpx.Client(timeout=25,follow_redirects=True) as c:
            r=c.get('https://www.youtube.com/watch',params={'v':key,'hl':'vi'});r.raise_for_status();match=re.search(r'var ytInitialPlayerResponse = (\{.*?\});',r.text)
            if not match:return {'video_id':key,'status':'missing_player_metadata'}
            d=json.loads(match[1]);v=d.get('videoDetails',{});m=d.get('microformat',{}).get('playerMicroformatRenderer',{});caps=d.get('captions',{}).get('playerCaptionsTracklistRenderer',{})
            o=c.get('https://www.youtube.com/oembed',params={'url':'https://www.youtube.com/watch?v='+key,'format':'json'})
            result={'video_id':key,'status':'metadata_checked','title':v.get('title'),'channel':v.get('author'),'channel_id':v.get('channelId'),'description':v.get('shortDescription',''),'duration':v.get('lengthSeconds'),'published_at':m.get('publishDate'),'family_safe':m.get('isFamilySafe'),'playability':d.get('playabilityStatus',{}),'oembed_status':o.status_code,'oembed':o.json() if o.status_code==200 else None,'caption_languages':[c.get('languageCode') for c in caps.get('captionTracks',[])],'translation_vi_available':any(c.get('languageCode')=='vi' for c in caps.get('translationLanguages',[])),'caption_tracks':caps.get('captionTracks',[]),'storyboards':d.get('storyboards',{})}
    except Exception as e:result={'video_id':key,'status':'metadata_network_error','error_type':type(e).__name__}
    file.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');return result

def main():
    state=load();short=json.loads((R/'docs/video-research/shortlist.json').read_text(encoding='utf8'))['choices'];byid={r['career_id']:r for r in state['careers']}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(inspect,key):cid for cid,key in short.items()}
        for i,f in enumerate(as_completed(futures),1):
            cid=futures[f];result=f.result();row=byid[cid];row['selection']={k:result.get(k) for k in ('video_id','status','title','channel','channel_id','duration','published_at','family_safe','caption_languages','translation_vi_available')};row['selection']['url']='https://www.youtube.com/watch?v='+short[cid];row['selection']['metadata_playability']=result.get('playability',{}).get('status');row['status']='needs_playback_and_content_review';save(state)
            if i%25==0 or i==len(short):print(json.dumps({'metadata_checked':i,'total_shortlisted':len(short),'published_added':0}),flush=True)
if __name__=='__main__':main()
