import copy,json,os,unittest
from unittest.mock import patch
from pathlib import Path
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app import app
import career_videos as v
from scripts.import_youtube import youtube_id,candidate

class VideoTests(unittest.TestCase):
    def sample(self):return v.videos()[0].model_dump(mode='json')
    def test_actual_data_and_career_pair_uniqueness(self):
        rows=v.videos();self.assertEqual(len(rows),3);self.assertEqual(sum(r.verification_status=='verified' for r in rows),2)
        a=self.sample();b={**a,'id':'other-internal-id'}
        with self.assertRaises(ValidationError):v.VideoCatalog(items=[a,b])
    def test_reject_unknown_career_and_unsafe_urls(self):
        for fields in [{'career_id':'not-real'},{'youtube_video_id':'bad'},{'youtube_url':'https://evil.test/watch?v=_WQ_VV4pXPc'},
                       {'youtube_url':'http://www.youtube.com/watch?v=_WQ_VV4pXPc'},{'thumbnail_url':'https://i.ytimg.com/vi/dt6td67yF9E/hqdefault.jpg'},
                       {'source_platform':'facebook'}]:
            with self.subTest(fields=fields),self.assertRaises(ValidationError):v.CareerVideo.model_validate({**self.sample(),**fields})
    def test_verified_requires_content_review_and_real_metadata(self):
        for fields in [{'reviewed_by':None},{'verification_method':'title only'},{'source_reliability':'unverified'},{'channel_name':None},{'thumbnail_url':None},{'featured_tasks':[]}]:
            with self.subTest(fields=fields),self.assertRaises(ValidationError):v.CareerVideo.model_validate({**self.sample(),**fields})
    def test_pending_rejected_unavailable_and_unknown_never_public(self):
        sample=self.sample()
        for status in ['candidate','pending_review','rejected','unavailable']:
            with patch.object(v,'videos',return_value=[v.CareerVideo.model_validate({**sample,'verification_status':status})]):self.assertEqual(v.public_for(sample['career_id']),[])
        for availability in ['unknown','unavailable']:
            with patch.object(v,'videos',return_value=[v.CareerVideo.model_validate({**sample,'availability_status':availability})]):self.assertEqual(v.public_for(sample['career_id']),[])
    def test_embed_disabled_keeps_only_real_external_link(self):
        row=v.CareerVideo.model_validate({**self.sample(),'embeddable':False,'availability_status':'embed_disabled'})
        with patch.object(v,'videos',return_value=[row]):
            result=v.public_for(row.career_id)[0];self.assertFalse(result['embeddable']);self.assertEqual(result['youtube_url'],row.youtube_url)
    def test_public_routes_filter_candidates_without_fetching_youtube(self):
        with patch('httpx.Client.get',side_effect=AssertionError('No provider fetch on page load')),TestClient(app) as client:
            items=client.get('/api/career-stories').json()['items'];self.assertEqual(len(items),200)
            self.assertEqual(sum(r['video_count'] for r in items),2)
            for cid,count in [('lap-trinh',1),('thiet-ke',1),('kiem-sat-vien',0),('dau-bep',0)]:
                r=client.get('/api/career-videos/'+cid);self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['items']),count)
                self.assertNotIn('verification_method',r.text)
            self.assertEqual(client.get('/api/career-videos/no-such-career').status_code,404)
    def test_manual_import_only_fixed_youtube_hosts(self):
        good='https://www.youtube.com/watch?v=_WQ_VV4pXPc'
        self.assertEqual(youtube_id(good),'_WQ_VV4pXPc');self.assertEqual(youtube_id('https://youtu.be/dt6td67yF9E?t=2'),'dt6td67yF9E')
        for url in ['http://www.youtube.com/watch?v=_WQ_VV4pXPc','https://youtube.com.evil.test/watch?v=_WQ_VV4pXPc','https://youtube.com@127.0.0.1/','https://127.0.0.1/','https://www.youtube.com:8080/watch?v=_WQ_VV4pXPc','https://www.youtube.com/watch?v=bad']:
            with self.subTest(url=url),self.assertRaises(ValueError):youtube_id(url)
    def test_import_oembed_does_not_approve_or_invent_duration(self):
        import httpx
        def fake(client,url,**kwargs):
            if url!='https://www.youtube.com/oembed':raise AssertionError('Unexpected external URL')
            return httpx.Response(200,json={'title':'Software Developers Career Video','author_name':'CareerOneStop','thumbnail_url':'https://i.ytimg.com/vi/_WQ_VV4pXPc/hqdefault.jpg'},request=httpx.Request('GET',url))
        with patch.dict(os.environ,{'YOUTUBE_DATA_API_KEY':''}),patch('httpx.Client.get',fake):
            row=candidate('lap-trinh','https://youtu.be/_WQ_VV4pXPc');self.assertEqual(row.verification_status,'pending_review');self.assertIsNone(row.duration_seconds);self.assertIsNone(row.embeddable)

if __name__=='__main__':unittest.main()
