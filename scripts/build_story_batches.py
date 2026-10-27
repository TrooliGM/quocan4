"""Biên dịch bản thảo có biên tập thành JSON runtime; không dùng AI/API.

Mỗi dòng có 13 trường: ID|tựa|tên|nơi|mở|tình huống1|A1|B1|tình huống2|A2|B2|kết|suy ngẫm.
Mỗi lựa chọn: hành động ~ lý do ~ hệ quả. Không tự sinh tình huống nếu thiếu bản thảo.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from career_library import catalog

ARTS = {'technology':['planning','coding','testing','demo','review'],
        'health':['consult','conference','prescription','consult','review'],
        'education':['lesson','classroom','mentoring','marking','review'],
        'engineering':['brief','system','records','monitoring','review'],
        'business':['brief','planning','records','feedback','review'],
        'finance':['brief','records','system','records','review'],
        'design':['brief','sketch','layout','feedback','review'],
        'media':['editorial','interview','editing','feedback','review'],
        'public-service':['brief','records','planning','review','records'],
        'environment':['sampling','records','system','monitoring','review'],
        'hospitality':['brief','planning','planning','feedback','review'],
        'science':['records','records','system','review','records']}

def compile_batch(number):
    careers = catalog().careers[(number-1)*50:number*50]
    path=Path(__file__).parent/'story-drafts'/f'batch-{number}.txt'
    lines=[line for line in path.read_text(encoding='utf8').splitlines() if line.strip() and not line.startswith('#')]
    if len(lines)!=50: raise ValueError(f'Batch {number}: expected 50 authored rows, got {len(lines)}')
    result=[]
    for career,line in zip(careers,lines,strict=True):
        fields=line.split('|')
        if len(fields)!=13: raise ValueError(f'Wrong field count {len(fields)}: {career.career_id}')
        cid,title,name,place,opening,q1,a1,b1,q2,a2,b2,ending,reflection=fields
        if cid!=career.career_id: raise ValueError('Draft order/ID mismatch: '+cid)
        arts=ARTS[career.category_id]
        if career.category_id=='health' and cid!='bac-si':
            arts=['brief','records','planning','records','review']
        def choices(a,b):
            out=[]
            for i,text in enumerate((a,b)):
                parts=text.split('~')
                if len(parts)!=3: raise ValueError('Need action, feedback, consequence: '+cid)
                out.append(dict(choice_id=f'option-{i+1}',text=parts[0],feedback=parts[1],consequence=parts[2]))
            return out
        skill=career.skill_details
        def panel(i,heading,caption,speech,question='',options=None):
            detail=skill[i%len(skill)]
            return dict(scene_id=f'scene-{i+1}',title=heading,time=['07:45','09:15','11:00','14:00','16:30'][i],
                art=arts[i],caption=caption,speech=speech,
                skill=detail['skill'],skill_reason=detail['reason'],question=question,choices=options or [],
                next_scene_id=f'scene-{i+2}' if i<4 else None)
        scenes=[panel(0,title,opening,f'{name}: Hôm nay, mình cùng xem việc này được làm như thế nào nhé.'),
            panel(1,'Một lựa chọn lúc bắt tay vào việc',q1,f'{name}: Mỗi cách xử lý sẽ dẫn đến điều gì?',q1,choices(a1,b1)),
            panel(2,career.daily_tasks[2].rstrip('.'),career.typical_day[1]['activity']+' '+career.work_environment,
                  f'{name}: '+career.daily_tasks[1].rstrip('.')+' cần gắn với nhiệm vụ của cả nhóm.'),
            panel(3,'Khi công việc có thêm một nút thắt',q2,f'{name}: Mình cần giải thích được căn cứ của quyết định.',q2,choices(a2,b2)),
            panel(4,'Điều còn lại sau ca làm',ending,f'{name}: '+reflection)]
        result.append(dict(career_id=cid,name=career.name,title=title,character=name,workplace=place,intro=opening,
            scenes=scenes,takeaway=reflection+' '+career.description,
            reflection=[reflection,'Trong hai tình huống vừa gặp, thông tin nào khiến em muốn chọn lại cách xử lý?'],
            ai_questions=[f'Vì sao người làm nghề {career.name} cần cân nhắc tình huống: {q1}',f'Em có thể rèn {career.skills[0].lower()} bằng hoạt động an toàn nào ở trường?'],
            video_sources=[],version=2))
    out=Path(__file__).resolve().parents[1]/'data'/'stories';out.mkdir(exist_ok=True)
    (out/f'batch-{number}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(f'Compiled {number}: {len(result)} stories, no provider calls')

if __name__=='__main__':
    for arg in sys.argv[1:]: compile_batch(int(arg))
