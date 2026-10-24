"""Kiểm định cấu trúc/đặc trưng, không thay thế thẩm định chuyên gia."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from story_library import Story, ROOT
from career_library import catalog

def validate(numbers=(1,2,3,4)):
    result=[]
    for n in numbers:
        rows=json.loads((ROOT/f'batch-{n}.json').read_text(encoding='utf8'))
        expected=[c.career_id for c in catalog().careers[(n-1)*50:n*50]]
        assert [row['career_id'] for row in rows]==expected, 'Missing/duplicate/reordered IDs'
        for row in rows:
            story=Story.model_validate(row)
            serialized=json.dumps(row,ensure_ascii=False).lower()
            assert not any(s in serialized for s in ['lorem ipsum','todo','placeholder','tbd','điền nội dung']), story.career_id
            assert not story.video_sources, 'Video must be verified before publishing'
            assert all(len({c.feedback for c in s.choices})==len(s.choices) for s in story.scenes)
            result.append(row)
    assert len({s['title'] for s in result})==len(result), 'Duplicate titles'
    # Tình huống/mở/kết phải độc lập, không dùng bài giống nhau thay tên.
    for i in [0,1,3,4]:
        assert max(Counter(s['scenes'][i]['caption'] for s in result).values())==1, 'Repeated story content'
    if len(numbers)==4:
        assert len(result)==200
        assert {s['career_id'] for s in result}=={c.career_id for c in catalog().careers}
    return {'stories':len(result),'scenes':sum(len(s['scenes']) for s in result),
            'decisions':sum(bool(p['choices']) for s in result for p in s['scenes']),
            'verified_videos':0,'status':'PASS','professional_review':'editorial sample review, not all-career expert certification'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',type=int,action='append');args=p.parse_args()
    print(json.dumps(validate(args.batch or (1,2,3,4)),ensure_ascii=False))
