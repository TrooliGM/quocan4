import unittest
from advisor.conversation_context import plan_turn,bounded_history,public_search_query
from advisor.search_provider import needs_search
class ContextTests(unittest.TestCase):
 def test_intent_and_bounded_output(self):
  for message,intent in [('so sanh bac si va dieu duong','compare'),('lộ trình từng bước','plan'),('Mức lương ngành đó năm 2020','research')]:self.assertEqual(plan_turn({'messages':[]},message)['intent'],intent)
  self.assertLess(plan_turn({'messages':[]},'Nói ngắn gọn thôi')['max_tokens'],plan_turn({'messages':[]},'Phân tích sâu nghề này')['max_tokens'])
 def test_career_mode_is_not_dropped(self):
  s={'messages':[{'career_context':{'mode':'career_exploration','career_id':'kiem-sat-vien'}}]}
  self.assertEqual(plan_turn(s,'nghề đó làm gì?')['career_id'],'kiem-sat-vien')
 def test_bounded_history_preserves_roles_and_visible_recommendation(self):
  messages=[{'role':'user' if i%2 else 'assistant','content':'x'*2000} for i in range(30)]
  rows=bounded_history(messages);self.assertLessEqual(sum(len(r['content']) for r in rows),12000);self.assertEqual(rows[-1]['role'],'user')
  rows=bounded_history([{'role':'assistant','content':'Ba nghề','recommendations':[{'name':'Điều dưỡng'}]}]);self.assertIn('Điều dưỡng',rows[0]['content'])
 def test_reference_search_uses_public_topic_and_year_not_profile(self):
  s={'messages':[{'role':'assistant','content':'hello','survey':{'answers':['PRIVATE_SURVEY']*5}},{'role':'user','content':'Số liệu ngành Thủy lợi năm 2020'}],'profile':{'interests':['PRIVATE_PROFILE']}}
  query=public_search_query(s,'nganh do nam ay co bao cao gi?');self.assertIn('2020',query);self.assertIn('Thủy lợi',query);self.assertNotIn('PRIVATE',query)
 def test_sensitive_earlier_turn_is_not_copied_into_search(self):
  s={'messages':[{'role':'user','content':'Em tên là SECRET và thích nghề lương cao năm 2020'}]}
  self.assertNotIn('SECRET',public_search_query(s,'nghề đó năm ấy'))
 def test_search_routing_not_for_everything(self):
  self.assertTrue(needs_search('chinh sach va chung chi hanh nghe'));self.assertTrue(needs_search('thong tin tuyen sinh moi nhat'))
  for t in ['Chào bạn','Mình thích vẽ','2 + 2 bằng mấy?','Dựa trên hồ sơ của tôi']:self.assertFalse(needs_search(t))

 def test_simple_math_does_not_pull_career_or_survey_context(self):
  p=plan_turn({'messages':[]},'2 + 2 bằng mấy?');self.assertFalse(p['needs_career_reference']);self.assertFalse(p['needs_survey_context'])
