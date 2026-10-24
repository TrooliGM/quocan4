"""Nhập ứng viên bằng oEmbed hoặc YouTube Data API (nếu có key). Không tự phê duyệt.

python scripts/import_youtube.py --career-id lap-trinh --url URL --output artifacts/candidate.json
File output không thể ghi đè: nội dung phải được biên tập/rà soát trước khi vào catalog runtime.
"""
import argparse,json,os,re,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlparse,parse_qs,urlencode
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from career_videos import CareerVideo

def youtube_id(url):
    u=urlparse(url)
    if u.scheme!='https' or u.username or u.password or u.port or u.fragment:raise ValueError('Use a public HTTPS YouTube URL')
    if u.hostname=='youtu.be':key=u.path.lstrip('/')
    elif u.hostname in ('www.youtube.com','youtube.com','m.youtube.com') and u.path=='/watch':key=parse_qs(u.query).get('v',[''])[0]
    elif u.hostname in ('www.youtube.com','youtube.com') and u.path.startswith(('/shorts/','/embed/')):key=u.path.split('/')[2]
    else:raise ValueError('Only YouTube watch, shorts or shared links')
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',key):raise ValueError('Invalid YouTube ID')
    return key

def candidate(career_id,url):
    key=youtube_id(url);canonical='https://www.youtube.com/watch?v='+key
    row=dict(id=career_id+'-'+key.lower().replace('_','-'),career_id=career_id,youtube_video_id=key,youtube_url=canonical,
        video_type='career_introduction',verification_status='candidate')
    with httpx.Client(timeout=15,follow_redirects=False) as client:
        # Chỉ fetch endpoint cố định, không fetch URL người nhập, tránh SSRF.
        try:
            r=client.get('https://www.youtube.com/oembed',params={'url':canonical,'format':'json'});r.raise_for_status();o=r.json()
            row.update(title=o['title'],channel_name=o['author_name'],thumbnail_url=o.get('thumbnail_url'),
                verification_status='pending_review',last_checked_at=datetime.now(timezone.utc),
                verification_method='oEmbed metadata only; chưa kiểm nội dung, độ tuổi, truy cập hoặc quyền nhúng.')
        except (httpx.HTTPError,KeyError,ValueError):
            row['verification_method']='Không lấy được metadata; chưa xác minh. Không tự điền tiêu đề/kênh/thời lượng.'
        api_key=os.getenv('YOUTUBE_DATA_API_KEY','').strip()
        if api_key:
            try:
                r=client.get('https://www.googleapis.com/youtube/v3/videos',params={'part':'snippet,contentDetails,status','id':key,'key':api_key});r.raise_for_status()
                item=r.json().get('items',[None])[0]
                if item:
                    snippet=item['snippet'];status=item['status']
                    row.update(title=snippet['title'],channel_name=snippet['channelTitle'],channel_id=snippet['channelId'],
                        published_at=snippet.get('publishedAt','')[:10] or None,embeddable=status.get('embeddable'),
                        language=snippet.get('defaultAudioLanguage'),availability_status='available' if status.get('embeddable') else 'embed_disabled',
                        verification_status='pending_review',last_checked_at=datetime.now(timezone.utc))
                    length=re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',item['contentDetails'].get('duration',''))
                    if length:row['duration_seconds']=sum(int(v or 0)*n for v,n in zip(length.groups(),[3600,60,1])) or None
                    row['verification_method']='YouTube Data API metadata/status; vẫn cần kiểm nội dung, độ tuổi, liên quan nghề trước phê duyệt.'
            except (httpx.HTTPError,ValueError,KeyError,IndexError,TypeError):
                pass # Không ghi URL request có key hay response body ra log.
    return CareerVideo.model_validate(row)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--career-id',required=True);p.add_argument('--url',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    try:
        row=candidate(a.career_id,a.url)
        with Path(a.output).open('x',encoding='utf8') as out:out.write(row.model_dump_json(indent=2)+'\n')
        print(json.dumps({'status':row.verification_status,'career_id':row.career_id,'published':False}))
    except (ValueError,OSError):print('Import dừng: kiểm tra URL, career_id và đường dẫn output mới. Không in credentials.',file=sys.stderr);sys.exit(1)
