"""Metadata YouTube được biên tập tĩnh. Không gọi YouTube/API khi học sinh mở trang."""
import json,re
from datetime import datetime, date
from functools import lru_cache
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from career_library import find_career

VIDEO_PATH=Path(__file__).parent/'data'/'career-videos.json'
class CareerVideo(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id: str=Field(pattern=r'^[a-z0-9-]+$',max_length=120)
    career_id: str
    youtube_video_id: str=Field(pattern=r'^[A-Za-z0-9_-]{11}$')
    youtube_url: str
    source_platform: Literal['youtube']='youtube'
    title: str | None=None
    channel_name: str | None=None
    channel_id: str | None=Field(default=None,pattern=r'^UC[A-Za-z0-9_-]{22}$')
    description: str=Field(default='',max_length=800)
    thumbnail_url: str | None=None
    duration_seconds: int | None=Field(default=None,gt=0)
    published_at: date | None=None
    language: str | None=None
    subtitle_languages: list[str]=Field(default_factory=list,max_length=100)
    subtitle_note: str=Field(default='',max_length=320)
    review_scope: str=Field(default='',max_length=500)
    video_type: Literal['day_in_life','career_interview','workplace_documentary','career_introduction','educational_report']
    featured_tasks: list[str]=Field(default_factory=list,max_length=10)
    relevance_notes: str=''
    source_reliability: Literal['official_institution','established_media','educational_organization','professional_creator','unverified']='unverified'
    verification_status: Literal['candidate','pending_review','verified','rejected','unavailable']='candidate'
    verification_method: str=''
    verified_at: datetime | None=None
    reviewed_by: str | None=None
    embeddable: bool | None=None
    availability_status: Literal['available','unavailable','region_restricted','embed_disabled','unknown']='unknown'
    last_checked_at: datetime | None=None
    schema_version: Literal[1]=1

    @model_validator(mode='after')
    def trustworthy(self):
        if not find_career(self.career_id):raise ValueError('Unknown career ID')
        if self.youtube_url!='https://www.youtube.com/watch?v='+self.youtube_video_id:
            raise ValueError('Canonical YouTube URL required')
        if self.thumbnail_url and self.thumbnail_url not in [f'https://i.ytimg.com/vi/{self.youtube_video_id}/{kind}.jpg' for kind in ['hqdefault','mqdefault','maxresdefault','0']]:
            raise ValueError('Thumbnail must match this YouTube video')
        for stamp in [self.verified_at,self.last_checked_at]:
            if stamp and (stamp.tzinfo is None or stamp.utcoffset() is None):raise ValueError('UTC-aware timestamps required')
        if any(not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*',code) for code in self.subtitle_languages):
            raise ValueError('Invalid subtitle language code')
        if self.review_scope and self.verification_status=='verified' and self.language not in ('vi',None) and not self.subtitle_languages:
            raise ValueError('New foreign-language videos require checked subtitles')
        if self.verification_status=='verified':
            if not all([self.title,self.channel_name,self.thumbnail_url,self.description,self.featured_tasks,self.relevance_notes,self.verified_at,self.reviewed_by,self.last_checked_at,len(self.verification_method)>=40]):
                raise ValueError('Verified requires content review, metadata and evidence')
            if self.source_reliability=='unverified':raise ValueError('Unknown source cannot be approved')
        if self.availability_status=='embed_disabled' and self.embeddable is not False:raise ValueError('Embed status conflict')
        return self

class VideoCatalog(BaseModel):
    items: list[CareerVideo]
    @model_validator(mode='after')
    def unique(self):
        if len({v.id for v in self.items})!=len(self.items) or len({v.youtube_video_id for v in self.items})!=len(self.items):
            raise ValueError('Duplicate video ID or career/video pair')
        return self

@lru_cache(maxsize=1)
def videos():return VideoCatalog.model_validate(json.loads(VIDEO_PATH.read_text(encoding='utf8'))).items

def public_for(career_id):
    fields={'id','career_id','youtube_video_id','youtube_url','title','channel_name','description','thumbnail_url','duration_seconds','language','subtitle_languages','subtitle_note','review_scope','video_type','featured_tasks','embeddable','availability_status'}
    return [v.model_dump(mode='json',include=fields)
            for v in videos() if v.career_id==career_id and v.verification_status=='verified'
            and v.availability_status in ('available','embed_disabled','region_restricted')]
