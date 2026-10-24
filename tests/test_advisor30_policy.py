import unittest
from advisor.conversation_policy import address_style

class PolicyTests(unittest.TestCase):
    def test_latest_request_overrides_survey_and_persists(self):
        s={'messages':[{'role':'assistant','content':'hello','survey':{'address':'chị'}},{'role':'user','content':'Xưng mình–bạn nhé'},{'role':'assistant','content':'ok'}]}
        self.assertEqual(address_style(s,'Giải thích nghề này'),'mình–bạn')
        self.assertEqual(address_style(s,'Hãy dùng tôi–bạn'),'tôi–bạn')
        self.assertEqual(address_style(s,'Anh giải thích cho em'),'anh–em')
        self.assertIn('không gọi em',address_style(s,'Đừng gọi em nữa'))
        self.assertEqual(address_style({'messages':[]}), 'mình–bạn')
    def test_only_user_turns_in_this_conversation(self):
        s={'messages':[{'role':'assistant','content':'xưng tôi–bạn'}]}
        self.assertEqual(address_style(s),'mình–bạn')

    def test_negated_pair_cannot_override_explicit_choice(self):
        s={'messages':[{'role':'assistant','content':'hello','survey':{'address':'chị'}}]}
        msg='Từ bây giờ hãy xưng tôi–bạn, không dùng chị–em.'
        self.assertEqual(address_style(s,msg),'tôi–bạn')
        s['messages'].append({'role':'user','content':msg})
        self.assertEqual(address_style(s,'Tôi nên bắt đầu ra sao?'),'tôi–bạn')
        self.assertEqual(address_style(s,'Đừng dùng anh–em, hãy xưng mình–bạn'),'mình–bạn')
