"""Đối soát catalog offline. Không đánh đồng chưa gắn video với video lỗi phát.

python scripts/video_inventory.py --csv artifacts/video-inventory.csv
Không gọi YouTube/AI/database; trạng thái LIVE phải có báo cáo Chrome riêng.
"""
import argparse,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from career_library import catalog,CATEGORIES
from career_videos import videos,public_for

def inventory():
    result=[]
    for career in catalog().careers:
        rows=[r for r in videos() if r.career_id==career.career_id];visible=public_for(career.career_id)
        issues=[r for r in rows if r.availability_status in ('embed_disabled','unavailable','region_restricted')]
        result.append({'career_id':career.career_id,'name':career.name,'group':CATEGORIES[career.category_id],
                       'public_videos':len(visible),'attachment_status':'ATTACHED' if visible else 'NOT_ATTACHED',
                       'pending_review':sum(r.verification_status in ('candidate','pending_review') for r in rows),
                       'recorded_availability_issues':len(issues),'youtube_urls':' | '.join(v['youtube_url'] for v in visible)})
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',type=Path);args=p.parse_args();rows=inventory()
    if args.csv:
        with args.csv.open('x',encoding='utf-8-sig',newline='') as out:
            writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print(json.dumps({'careers':len(rows),'with_public_video':sum(r['public_videos']>0 for r in rows),
                      'without_public_video':sum(r['public_videos']==0 for r in rows),
                      'recorded_availability_issues':sum(r['recorded_availability_issues'] for r in rows),
                      'pending_review':sum(r['pending_review'] for r in rows),
                      'live_check_performed':False,'note':'NOT_ATTACHED không có nghĩa video bị lỗi. Lỗi trong metadata không thay cho kiểm thử phát LIVE.'},ensure_ascii=False))
if __name__=='__main__':main()
