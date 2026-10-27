"""Hợp đồng dữ liệu thư viện nghề; ID tương thích với Truyện nghề hiện có."""
import unicodedata
import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CATEGORIES = {
    'technology': 'Công nghệ thông tin và dữ liệu',
    'health': 'Y tế và chăm sóc sức khỏe',
    'education': 'Giáo dục và đào tạo',
    'engineering': 'Kỹ thuật và công nghiệp',
    'business': 'Kinh doanh và quản lý',
    'finance': 'Tài chính, kế toán và ngân hàng',
    'design': 'Thiết kế, nghệ thuật và sáng tạo',
    'media': 'Truyền thông và giải trí',
    'public-service': 'Luật, hành chính và dịch vụ công',
    'environment': 'Nông nghiệp, môi trường và tài nguyên',
    'hospitality': 'Du lịch, dịch vụ và khách sạn',
    'science': 'Khoa học, nghiên cứu và lĩnh vực khác',
}


def normalize_search(text):
    text = unicodedata.normalize('NFD', text.casefold().replace('đ', 'd'))
    return ' '.join(''.join(c for c in text if unicodedata.category(c) != 'Mn').split())


class Career(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)
    career_id: str = Field(pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$', max_length=80)
    name: str = Field(min_length=2, max_length=120)
    category_id: str
    short_description: str = Field(min_length=10, max_length=240)
    description: str = Field(min_length=20)
    daily_tasks: list[str] = Field(min_length=2)
    skills: list[str] = Field(min_length=2)
    related_subjects: list[str] = Field(min_length=1)
    work_environment: str = Field(min_length=10)
    challenges: list[str] = Field(min_length=1)
    keywords: list[str] = Field(min_length=1)
    typical_day: list[dict[str, str]] = Field(default_factory=list)
    skill_details: list[dict[str, str]] = Field(default_factory=list)
    learning_path: list[str] = Field(default_factory=list)
    professional_requirements: dict[str, str] = Field(default_factory=dict)
    sources: list[dict[str, str]] = Field(default_factory=list)
    profile_version: int = 1

    @field_validator('category_id')
    @classmethod
    def known_category(cls, value):
        if value not in CATEGORIES:
            raise ValueError('Unknown career category')
        return value

    @field_validator('daily_tasks', 'skills', 'related_subjects', 'challenges', 'keywords')
    @classmethod
    def meaningful_items(cls, values):
        if any(not value.strip() for value in values):
            raise ValueError('Empty career content')
        return [value.strip() for value in values]


class Catalog(BaseModel):
    careers: list[Career]

    @model_validator(mode='after')
    def unique_careers(self):
        for key in ('career_id', 'name'):
            values = [normalize_search(getattr(c, key)) for c in self.careers]
            if len(values) != len(set(values)):
                raise ValueError('Duplicate career '+key)
        return self

    def search(self, query='', category_id=None):
        query = normalize_search(query)
        return [c for c in self.careers if (not category_id or c.category_id == category_id)
                and query in normalize_search(' '.join([c.name, CATEGORIES[c.category_id],
                    c.short_description, *c.keywords]))]


@lru_cache(maxsize=1)
def catalog():
    rows = []
    for index in range(1, 5):
        rows.extend(json.loads((Path(__file__).parent/'data'/f'careers-{index}.json').read_text(encoding='utf-8')))
    result = Catalog(careers=rows)
    if len(result.careers) != 200:
        raise ValueError('Career catalog must contain exactly 200 careers')
    return result


def find_career(career_id):
    return next((c for c in catalog().careers if c.career_id == career_id), None)
