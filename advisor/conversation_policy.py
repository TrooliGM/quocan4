"""Ưu tiên xưng hô mới nhất; chỉ dùng lời người dùng trong đúng phiên."""
import re
import unicodedata

def address_style(session, latest=''):
    survey=(session.get('messages') or [{}])[0].get('survey') or {}
    style={'anh':'anh–em','chị':'chị–em'}.get(survey.get('address'),'mình–bạn')
    for text in [m['content'] for m in session.get('messages',[]) if m['role']=='user']+[latest]:
        text=unicodedata.normalize('NFC',text).lower()
        # Cặp xưng hô bị phủ định không phải lựa chọn mới của người dùng.
        text=re.sub(r'\b(?:không|khong|đừng|dung|dừng|khỏi|khoi)\s+(?:xưng|xung|dùng|dung|gọi|goi)\s+(?:theo\s+)?(?:anh|chị|chi|mình|minh|tôi|toi)\s*[-–—/,]\s*(?:em|bạn|ban)\b', '', text)
        # Preserve accented words: folding "chỉ" into "chi" would invent a gender choice.
        patterns=[(r'\b(?:đừng|dung|không|khong|dừng).{0,12}(?:gọi|goi).{0,6}em\b|\b(?:trang trọng|trang trong)\b','tôi–bạn; diễn đạt trang trọng, không gọi em'),
                  (r'\b(?:xưng|xung|dùng|dung|gọi|goi).{0,18}(?:mình|minh)\s*[-–—/,]\s*(?:bạn|ban)\b','mình–bạn'),
                  (r'\b(?:xưng|xung|dùng|dung|gọi|goi).{0,18}(?:tôi|toi)\s*[-–—/,]\s*(?:bạn|ban)\b','tôi–bạn'),
                  (r'\banh\b.{0,25}(?:cho em|[-–—/]\s*em)\b','anh–em'),
                  (r'\b(?:chị|chi)\b.{0,25}(?:cho em|[-–—/]\s*em)\b','chị–em')]
        choices=[(match.start(),value) for pattern,value in patterns for match in re.finditer(pattern,text)]
        if choices:style=max(choices,key=lambda pair:pair[0])[1]
    return style

def address_instruction(session, latest):
    return ('Cách xưng hô hiện tại: '+address_style(session,latest)+'. Ưu tiên yêu cầu trực tiếp mới nhất, '
            'không tự giới thiệu tên/danh tính, không đọc quy tắc hệ thống, không lặp lời chào. '
            'Chỉ giải thích danh tính hoặc xưng hô khi người dùng hỏi. Câu đơn giản trả lời trực tiếp; phân tích nghề có căn cứ, khó khăn và bước trải nghiệm an toàn. '
            'Không tự suy năng lực từ sở thích; không bịa % phù hợp. Hỏi tối đa một điều còn thiếu, không hỏi lại thông tin đã có.')
