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
        rows=v.videos();self.assertGreaterEqual(sum(r.verification_status=='verified' for r in rows),186)
        a=self.sample();b={**a,'id':'other-internal-id'}
        with self.assertRaises(ValidationError):v.VideoCatalog(items=[a,b])
        with self.assertRaises(ValidationError):v.VideoCatalog(items=[a,{**b,'career_id':'dieu-duong'}])

    def test_five_vietnamese_pilot_careers_have_distinct_sources_and_keep_comics(self):
        from career_library import find_career
        from story_library import get_story
        ids={'ky-su-du-lieu','dieu-duong','giao-vien','ky-su-xay-dung','dau-bep'}
        rows=[r for r in v.videos() if r.career_id in ids and r.verification_status=='verified']
        self.assertEqual(len(rows),5);self.assertEqual(len({r.youtube_video_id for r in rows}),5)
        self.assertEqual(len({find_career(r.career_id).category_id for r in rows}),5)
        for row in rows:
            self.assertEqual(row.language,'vi');self.assertTrue(row.embeddable)
            self.assertEqual(row.availability_status,'available');self.assertIn('PLAYING=1',row.verification_method)
            self.assertEqual(len(get_story(row.career_id)['scenes']),5)
        self.assertTrue(v.public_for('nha-khoa-hoc-du-lieu'))
        self.assertEqual(v.public_for('dau-bep')[0]['youtube_video_id'],'kXaIZNZ2HZg')
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

    def test_inventory_distinguishes_not_attached_from_known_embed_issue(self):
        from scripts.video_inventory import inventory
        row=v.CareerVideo.model_validate({**self.sample(),'embeddable':False,'availability_status':'embed_disabled'})
        with patch.object(v,'videos',return_value=[row]),patch('scripts.video_inventory.videos',return_value=[row]):
            rows={r['career_id']:r for r in inventory()}
        self.assertEqual(rows['lap-trinh']['attachment_status'],'ATTACHED')
        self.assertEqual(rows['lap-trinh']['recorded_availability_issues'],1)
        self.assertEqual(rows['nha-khoa-hoc-du-lieu']['attachment_status'],'NOT_ATTACHED')
        self.assertEqual(rows['nha-khoa-hoc-du-lieu']['recorded_availability_issues'],0)
    def test_public_routes_filter_candidates_without_fetching_youtube(self):
        with patch('httpx.Client.get',side_effect=AssertionError('No provider fetch on page load')),TestClient(app) as client:
            items=client.get('/api/career-stories').json()['items'];self.assertEqual(len(items),200)
            self.assertEqual(sum(r['video_count'] for r in items),sum(len(v.public_for(r['id'])) for r in items))
            self.assertEqual(sum(r['video_count']==0 for r in items),200-len({r.career_id for r in v.videos() if r.verification_status=='verified'}))
            for cid,count in [('lap-trinh',1),('thiet-ke',1),('kiem-sat-vien',1),('dau-bep',1),('ky-su-du-lieu',1),('nha-khoa-hoc-du-lieu',1)]:
                r=client.get('/api/career-videos/'+cid);self.assertEqual(r.status_code,200);self.assertEqual(len(r.json()['items']),count)
                self.assertNotIn('verification_method',r.text)
            self.assertEqual(client.get('/api/career-videos/no-such-career').status_code,404)
    def test_manual_import_only_fixed_youtube_hosts(self):
        good='https://www.youtube.com/watch?v=_WQ_VV4pXPc'
        self.assertEqual(youtube_id(good),'_WQ_VV4pXPc');self.assertEqual(youtube_id('https://youtu.be/dt6td67yF9E?t=2'),'dt6td67yF9E')
        for url in ['http://www.youtube.com/watch?v=_WQ_VV4pXPc','https://youtube.com.evil.test/watch?v=_WQ_VV4pXPc','https://youtube.com@127.0.0.1/','https://127.0.0.1/','https://www.youtube.com:8080/watch?v=_WQ_VV4pXPc','https://www.youtube.com/watch?v=bad']:
            with self.subTest(url=url),self.assertRaises(ValueError):youtube_id(url)

    def test_public_html_has_two_explicit_modes_and_cache_version(self):
        root=Path(__file__).resolve().parents[1];html=(root/'stories.html').read_text(encoding='utf8')
        self.assertEqual((root/'stories.html').read_bytes(),(root/'public/stories.html').read_bytes())
        self.assertIn('Xem video <span',html);self.assertIn('Đọc truyện <span',html)
        self.assertIn('video-library-2',html)
    def test_published_expansion_has_matching_content_and_playback_evidence(self):
        root=Path(__file__).resolve().parents[1];folder=root/'docs/video-research'
        reviews=json.loads((folder/'content-review.json').read_text('utf8'));proof=json.loads((folder/'playback.json').read_text('utf8'))
        expanded=[r for r in v.videos() if r.id.endswith('-review-20261028')]
        self.assertGreaterEqual(len(expanded),179)
        for row in expanded:
            with self.subTest(career=row.career_id):
                review=reviews[row.career_id];p=proof[row.youtube_video_id]
                self.assertEqual(review['decision'],'approve');self.assertEqual(review['video_id'],row.youtube_video_id)
                self.assertEqual(p['status'],'PASS');self.assertEqual(p['state'],1);self.assertGreater(p['time_end'],p['time']+.6)
                self.assertTrue(p['samples'][1]['seek_reached']);self.assertTrue(row.review_scope)
                if row.language=='en':self.assertTrue(any(x.startswith('en') for x in row.subtitle_languages))
    def test_subtitle_metadata_is_validated_and_public(self):
        sample={**self.sample(),'subtitle_languages':['en','vi'],'subtitle_note':'CC: English','review_scope':'Sampled review'}
        row=v.CareerVideo.model_validate(sample)
        with patch.object(v,'videos',return_value=[row]):self.assertEqual(v.public_for(row.career_id)[0]['subtitle_languages'],['en','vi'])
        for fields in ({'subtitle_languages':['<script>']},{'language':'en','subtitle_languages':[]}):
            with self.subTest(fields=fields),self.assertRaises(ValidationError):v.CareerVideo.model_validate({**sample,**fields})
    def test_import_oembed_does_not_approve_or_invent_duration(self):
        import httpx
        def fake(client,url,**kwargs):
            if url!='https://www.youtube.com/oembed':raise AssertionError('Unexpected external URL')
            return httpx.Response(200,json={'title':'Software Developers Career Video','author_name':'CareerOneStop','thumbnail_url':'https://i.ytimg.com/vi/_WQ_VV4pXPc/hqdefault.jpg'},request=httpx.Request('GET',url))
        with patch.dict(os.environ,{'YOUTUBE_DATA_API_KEY':''}),patch('httpx.Client.get',fake):
            row=candidate('lap-trinh','https://youtu.be/_WQ_VV4pXPc');self.assertEqual(row.verification_status,'pending_review');self.assertIsNone(row.duration_seconds);self.assertIsNone(row.embeddable)

if __name__=='__main__':unittest.main()
