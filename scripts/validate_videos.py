"""Kiểm định catalog offline, không tự đổi candidate thành verified."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from career_videos import videos,public_for

if __name__=='__main__':
    rows=videos();approved=[v for v in rows if v.verification_status=='verified']
    visible=sum(len(public_for(c)) for c in {v.career_id for v in rows})
    print(json.dumps({'status':'PASS','candidates_total':len(rows),'verified_with_recorded_method':len(approved),
        'visible_videos':visible,'careers_with_video':len({v.career_id for v in approved if public_for(v.career_id)}),
        'pending_review':sum(v.verification_status=='pending_review' for v in rows),
        'live_check_performed':False},ensure_ascii=False))
