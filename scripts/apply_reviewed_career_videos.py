"""Apply explicit human/editorial decisions only; never approve search results automatically.

Requires matching content-review.json AND genuine PLAYING/clock evidence.
No network, database, AI, or publication is performed by this script.
"""
import json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from career_videos import VideoCatalog

def main():
    folder=R/'docs/video-research';raw=json.loads((R/'data/career-videos.json').read_text('utf8'))
    reviewed=json.loads((folder/'content-review.json').read_text('utf8'));proof=json.loads((folder/'playback.json').read_text('utf8'))
    bycareer={v['career_id'] for v in raw['items'] if v['verification_status']=='verified'};known={v['youtube_video_id'] for v in raw['items']};added=[];blocked={}
    for cid,decision in reviewed.items():
        if cid in bycareer or decision['decision']!='approve':continue
        key=decision['video_id'];p=proof.get(key,{})
        if p.get('status')!='PASS' or p.get('state')!=1 or p.get('time_end',0)<=p.get('time',0)+.6:
            blocked[cid]='Playback chưa được xác nhận';continue
        if key in known:raise ValueError('A video cannot be reused for another career: '+cid)
        m=json.loads((R/'artifacts/video-research/metadata'/f'{key}.json').read_text('utf8'))
        languages=list(dict.fromkeys(x for x in m.get('caption_languages',[]) if isinstance(x,str) and re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*',x)))
        english_source=any(word in m['channel'] for word in ['CareerOneStop','Life at Google','Cambridge University','George Mason','Siemens','GPB Education','Tahatū','Spreetail','BBC','European Patent','alisWebsite','Scripps','Devlin Peck','WSB','SEH'])
        language=decision.get('language') or ('en' if english_source else 'vi')
        if language=='en' and not any(x.startswith('en') for x in languages):
            blocked[cid]='Chưa xác minh phụ đề phù hợp cho video ngoại ngữ';continue
        # Fail closed if the actual mid-video observation did not reach the requested segment.
        if len(p.get('samples',[]))<2 or not p['samples'][1].get('seek_reached'):
            blocked[cid]='Chưa quan sát được đoạn giữa; không tự suy từ thời gian seek';continue
        auto=any(t.get('kind')=='asr' and t.get('languageCode')==language for t in m.get('caption_tracks',[]))
        subtitle_note=('Phụ đề tiếng Anh'+(' tự động' if auto else '')+' trên YouTube; có thể bật CC. Bối cảnh quốc tế, quy định/nghề nghiệp có thể khác Việt Nam.' if language=='en' else 'Có phụ đề tiếng Việt tự động trên YouTube; có thể có lỗi nhận dạng.' if 'vi' in languages and auto else 'Có phụ đề tiếng Việt trên YouTube.' if 'vi' in languages else 'Chưa ghi nhận phụ đề từ YouTube; xem hình và chữ hướng dẫn trong video.')
        title=m['title'];source=m['channel'];scope='Đã rà mô tả nguồn và hai đoạn hình/phụ đề mẫu đầu–giữa, chưa xem/nghe toàn bộ. Không thấy nội dung đồ họa nhạy cảm trong các mẫu đã rà.'
        raw['items'].append({
            'id':cid+'-review-20261028','career_id':cid,'youtube_video_id':key,'youtube_url':'https://www.youtube.com/watch?v='+key,
            'source_platform':'youtube','title':title,'channel_name':source,'channel_id':m['channel_id'],
            'description':decision['relevance_notes'][:800],'thumbnail_url':f'https://i.ytimg.com/vi/{key}/hqdefault.jpg',
            'duration_seconds':int(m['duration']),'published_at':m['published_at'][:10] if m.get('published_at') else None,
            'language':language,'subtitle_languages':languages,'subtitle_note':subtitle_note,'review_scope':scope,
            'video_type':decision.get('video_type') or ('career_introduction' if source=='CareerOneStop' else 'career_interview'),
            'featured_tasks':decision['featured_tasks'],'relevance_notes':decision['relevance_notes'],
            'source_reliability':decision['source_reliability'],'verification_status':'verified',
            'verification_method':f"Chrome LIVE YouTube IFrame API PLAYING=1, clock {p['time']:.2f}→{p['time_end']:.2f}s; video ID matched. Reviewed actual sample frames/captions and publisher description; not full audio. Evidence docs/video-research/playback.json + content-review.json.",
            'verified_at':decision['reviewed_at'],'reviewed_by':'Codex – rà mẫu có ghi giới hạn',
            'embeddable':True,'availability_status':'available','last_checked_at':p['checked_at'],'schema_version':1
        });known.add(key);added.append(cid)
    VideoCatalog.model_validate(raw)
    (R/'data/career-videos.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n','utf8')
    (folder/'integration-receipt.json').write_text(json.dumps({'added':added,'blocked':blocked,'verified_total':sum(v['verification_status']=='verified' for v in raw['items']),'inherited_verified':7,'automatic_approval':False},ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps({'added_this_run':len(added),'blocked':len(blocked),'verified_total':sum(v['verification_status']=='verified' for v in raw['items'])}))

if __name__=='__main__':main()
