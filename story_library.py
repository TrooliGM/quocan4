"""Truyện 2.0 tĩnh; chỉ đọc một đợt khi mở một truyện, không gọi provider/database."""
import json
from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, model_validator
from career_library import catalog, CATEGORIES, find_career

ROOT = Path(__file__).parent / 'data' / 'stories'

class Choice(BaseModel):
    model_config = ConfigDict(extra='forbid')
    choice_id: str
    text: str = Field(min_length=8)
    feedback: str = Field(min_length=25)
    consequence: str = Field(min_length=20)

class Scene(BaseModel):
    model_config = ConfigDict(extra='forbid')
    scene_id: str
    title: str = Field(min_length=5)
    time: str
    art: str
    caption: str = Field(min_length=60)
    speech: str = Field(min_length=8)
    skill: str = Field(min_length=5)
    skill_reason: str = Field(min_length=20)
    question: str = ''
    choices: list[Choice] = Field(default_factory=list, max_length=3)
    next_scene_id: str | None

class Story(BaseModel):
    model_config = ConfigDict(extra='forbid')
    career_id: str
    name: str
    title: str = Field(min_length=8)
    character: str = Field(min_length=2)
    workplace: str = Field(min_length=12)
    intro: str = Field(min_length=40)
    scenes: list[Scene] = Field(min_length=4, max_length=6)
    takeaway: str = Field(min_length=50)
    reflection: list[str] = Field(min_length=2)
    ai_questions: list[str] = Field(min_length=2)
    video_sources: list[dict] = Field(max_length=0) # Chỉ mở whitelist khi có video đã thẩm định.
    version: int = Field(default=2, ge=2, le=2)

    @model_validator(mode='after')
    def coherent(self):
        career = find_career(self.career_id)
        if not career or career.name != self.name:
            raise ValueError('Career ID/name mismatch')
        ids = [s.scene_id for s in self.scenes]
        if len(ids) != len(set(ids)) or sum(bool(s.choices) for s in self.scenes) < 2:
            raise ValueError('Duplicate scenes or too few decisions')
        for i, s in enumerate(self.scenes):
            if s.next_scene_id != (ids[i+1] if i+1 < len(ids) else None):
                raise ValueError('Broken sequence')
            if s.choices and (not s.question or len(s.choices) < 2 or len({c.choice_id for c in s.choices}) != len(s.choices)):
                raise ValueError('Invalid decision')
        return self

def summaries():
    # Không parse nội dung 200 truyện để dựng danh sách.
    from career_videos import public_for
    result=[]
    for c in catalog().careers:
        approved=public_for(c.career_id)
        result.append(dict(id=c.career_id,name=c.name,category=CATEGORIES[c.category_id],
            category_id=c.category_id,scenes=5,version=2,short_description=c.short_description,
            video_count=len(approved),cover_video=approved[0] if approved else None))
    return result

@lru_cache(maxsize=4)
def batch(number):
    rows = json.loads((ROOT / f'batch-{number}.json').read_text(encoding='utf-8'))
    return {row['career_id']: Story.model_validate(row).model_dump() for row in rows}

def get_story(career_id):
    careers = catalog().careers
    position = next((i for i,c in enumerate(careers) if c.career_id == career_id), None)
    if position is None:
        return None
    row = batch(position // 50 + 1).get(career_id)
    if not row:
        return None
    career = careers[position]
    return {**row, 'id': career_id, 'category': CATEGORIES[career.category_id], 'short_description':career.short_description,
            'category_id': career.category_id, 'skills': career.skills,
            'first_step': career.learning_path[-1], 'sources': career.sources,
            'note': 'Nhân vật và tình huống hư cấu do La Bàn biên soạn. Giờ làm minh họa; nhiệm vụ thay đổi theo vị trí và nơi làm việc. Đây là trải nghiệm hướng nghiệp, không phải hướng dẫn hành nghề.'}
