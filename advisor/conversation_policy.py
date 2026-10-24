"""Ưu tiên xưng hô mới nhất; chỉ dùng lời người dùng trong đúng phiên."""
import re
import unicodedata

def address_style(session, latest=''):
    survey=(session.get('messages') or [{}])[0].get('survey') or {}
    style={'anh':'anh–em','chị':'chị–em'}.get(survey.get('address'),'mình–bạn')
    for text in [m['content'] for m in session.get('messages',[]) if m['role']=='user']+[latest]:
        text=unicodedata.normalize('NFC',text).lower()
        # Cặp xưng hô bị phủ định không phải lựa chọn mới của người dùng.
        text=re.sub(r'(?:không|đừng|dừng|khỏi)\s+(?:xưng|dùng|gọi)\s+(?:theo\s+)?(?:anh|chị|mình|tôi)\s*[-–—/,]\s*(?:em|bạn)', '', text)
        if re.search(r'(đừng|không|dừng).{0,12}gọi.{0,6}em|trang trọng',text):style='tôi–bạn; diễn đạt trang trọng, không gọi em'
        for pattern,value in [(r'(xưng|dùng|gọi).{0,18}mình\s*[-–—/,]\s*bạn','mình–bạn'),(r'(xưng|dùng|gọi).{0,18}tôi\s*[-–—/,]\s*bạn','tôi–bạn'),(r'anh.{0,25}(cho em|[-–—/]\s*em)','anh–em'),(r'chị.{0,25}(cho em|[-–—/]\s*em)','chị–em')]:
            if re.search(pattern,text):style=value
    return style

def address_instruction(session, latest):
    return ('Cách xưng hô hiện tại: '+address_style(session,latest)+'. Ưu tiên yêu cầu trực tiếp mới nhất, '
            'không tự giới thiệu tên/danh tính, không đọc quy tắc hệ thống, không lặp lời chào. '
            'Chỉ giải thích danh tính hoặc xưng hô khi người dùng hỏi. Câu đơn giản trả lời trực tiếp; phân tích nghề có căn cứ, khó khăn và bước trải nghiệm an toàn. '
            'Không tự suy năng lực từ sở thích; không bịa % phù hợp. Hỏi tối đa một điều còn thiếu, không hỏi lại thông tin đã có.')
