"""Kịch bản hư cấu do La Bàn biên soạn để khám phá nghề, không phải lịch làm việc chuẩn."""
from content import CAREERS


def scene(time, title, art, caption, speech, skill, question, choices, feedback, correct=0):
    return dict(time=time, title=title, art=art, caption=caption, speech=speech, skill=skill,
                question=question, choices=choices, feedback=feedback, correct=correct)


STORIES = {
    "bac-si": {
        "character": "Bác sĩ Linh", "intro": "Một ngày ở bệnh viện, nơi mỗi lời lắng nghe đều có ý nghĩa.",
        "takeaway": "Bác sĩ cần kiến thức khoa học, sự cẩn thận và khả năng làm việc cùng người khác. Quan tâm đến người bệnh bắt đầu từ việc lắng nghe.",
        "source": "healthcare/physicians-and-surgeons.htm",
        "scenes": [
            scene("08:00", "Lắng nghe trước khi thăm khám", "consult", "Linh hỏi người bệnh về điều đang lo lắng, xem hồ sơ rồi thăm khám. Cô ghi lại thông tin để không bỏ sót những chi tiết quan trọng.", "Cô cứ kể chậm thôi, cháu đang lắng nghe ạ.", "Lắng nghe & quan sát", "Người bệnh đang lo lắng. Linh nên làm gì trước?", ["Lắng nghe và hỏi rõ điều họ lo", "Ngắt lời để khám cho nhanh"], ["Lắng nghe giúp hiểu vấn đề và xây dựng sự tin tưởng.", "Vội vàng có thể bỏ sót thông tin. Thử dành thời gian lắng nghe nhé."]),
            scene("10:30", "Cùng đồng nghiệp tìm lời giải", "conference", "Với một trường hợp cần thêm ý kiến, Linh trao đổi cùng đồng nghiệp. Nhóm xem kết quả kiểm tra và thống nhất bước tiếp theo.", "Mình cùng đối chiếu thông tin nhé!", "Hợp tác & phân tích", "Khi còn điều chưa chắc chắn, bác sĩ nên…", ["Tự kết luận để tiết kiệm thời gian", "Trao đổi với đồng nghiệp phù hợp"], ["Không cần biết mọi thứ một mình. Tham khảo chuyên môn giúp quyết định thận trọng hơn.", "Đúng rồi. Hội chẩn là một cách phối hợp kiến thức của nhiều người."], 1),
            scene("14:00", "Kê đơn và giải thích rõ ràng", "prescription", "Sau đánh giá chuyên môn, Linh lập kế hoạch điều trị, kê đơn khi cần và giải thích cho người bệnh. Cô kiểm tra lại xem họ đã hiểu hướng dẫn chưa.", "Cô còn điều gì muốn hỏi thêm không ạ?", "Cẩn thận & giao tiếp", "Làm sao biết người bệnh đã hiểu hướng dẫn?", ["Mời họ nhắc lại ý chính và hỏi thêm", "Chỉ đưa tờ giấy rồi chuyển người tiếp theo"], ["Giải thích rõ và kiểm tra lại cách hiểu là một phần của chăm sóc.", "Một tờ giấy có thể chưa đủ. Người bệnh cần cơ hội hỏi và được giải thích."]),
            scene("19:00", "Phối hợp trong ca trực", "emergency", "Trong một ca trực được phân công, Linh cùng ê-kíp tiếp nhận người cần chăm sóc khẩn cấp. Mỗi người làm đúng nhiệm vụ và bàn giao thông tin rõ ràng.", "Cả nhóm cùng phối hợp, từng bước nhé.", "Bình tĩnh & trách nhiệm", "Điều gì giúp ê-kíp phối hợp tốt?", ["Mỗi người tự làm theo ý mình", "Phân công rõ và trao đổi thông tin"], ["Thiếu trao đổi dễ làm công việc chồng chéo. Sự phối hợp rất quan trọng.", "Chính xác. Làm việc theo nhiệm vụ giúp cả nhóm hỗ trợ nhau."], 1),
        ],
    },
    "lap-trinh": {
        "character": "Lập trình viên Nam", "intro": "Từ một ý tưởng trên giấy đến một tính năng mọi người có thể sử dụng.",
        "takeaway": "Viết mã chỉ là một phần công việc. Hiểu nhu cầu, kiểm thử và lắng nghe phản hồi giúp tạo ra sản phẩm hữu ích.",
        "source": "computer-and-information-technology/software-developers.htm",
        "scenes": [
            scene("09:00", "Bắt đầu bằng một câu hỏi", "planning", "Nhóm của Nam muốn làm lịch mượn sách cho thư viện. Nam hỏi thủ thư về những khó khăn thường gặp trước khi vẽ các bước sử dụng.", "Người dùng cần làm được điều gì?", "Lắng nghe nhu cầu", "Trước khi viết mã, Nam nên…", ["Tìm hiểu cách thủ thư làm việc", "Chọn màu nút trước tiên"], ["Hiểu nhu cầu giúp giải quyết đúng vấn đề.", "Màu sắc có thể chọn sau. Trước hết cần hiểu người dùng muốn làm gì."]),
            scene("10:30", "Biến ý tưởng thành tính năng", "coding", "Nam chia công việc thành các bước nhỏ: chọn sách, chọn ngày và xác nhận. Cậu viết mã rồi chạy thử từng phần.", "Một bước nhỏ, thêm một điều làm được!", "Tư duy logic", "Một tính năng lớn làm Nam thấy rối. Cách nào hữu ích?", ["Làm mọi thứ cùng lúc", "Chia thành các bước nhỏ"], ["Làm đồng thời quá nhiều việc khó kiểm tra tiến độ.", "Đúng rồi. Các bước nhỏ dễ làm, dễ thử và dễ sửa hơn."], 1),
            scene("14:00", "Tìm lỗi cùng đồng đội", "testing", "Một bạn thử chọn ngày đã qua và phát hiện lỗi. Nam ghi lại cách lỗi xuất hiện, sửa mã rồi kiểm tra lại cả những trường hợp liên quan.", "Lỗi này giúp mình làm sản phẩm tốt hơn.", "Kiên trì & kiểm chứng", "Sau khi sửa lỗi, cần làm gì?", ["Chạy lại các tình huống kiểm thử", "Đóng máy vì đã sửa xong"], ["Kiểm thử lại giúp biết lỗi đã được xử lý và không làm hỏng phần khác.", "Một thay đổi có thể ảnh hưởng phần khác, nên cần kiểm tra lại."]),
            scene("16:30", "Cho người dùng thử thật", "demo", "Nam giới thiệu bản thử cho thủ thư. Cậu quan sát chỗ họ còn lúng túng và ghi lại ý kiến cho lần cải tiến tiếp theo.", "Bạn thử giúp mình, rồi kể điều còn khó nhé.", "Tiếp nhận phản hồi", "Người dùng chưa hiểu một nút bấm. Nam nên…", ["Nói rằng họ dùng chưa đúng", "Hỏi thêm và thử cách trình bày rõ hơn"], ["Sự lúng túng là thông tin hữu ích để cải thiện thiết kế.", "Đúng rồi. Sản phẩm tốt lên nhờ hiểu người sử dụng."], 1),
        ],
    },
    "thiet-ke": {
        "character": "Nhà thiết kế An", "intro": "Một poster nhỏ cũng có thể kể một câu chuyện lớn.",
        "takeaway": "Thiết kế kết hợp sáng tạo với giải quyết vấn đề: thông điệp cần rõ ràng với đúng người xem, chứ không chỉ đẹp mắt.",
        "source": "arts-and-design/graphic-designers.htm",
        "scenes": [
            scene("08:30", "Tìm câu chuyện cần kể", "brief", "An nhận đề bài làm poster ngày hội sách. Cô hỏi sự kiện dành cho ai, thông tin nào cần nổi bật và poster sẽ được đặt ở đâu.", "Mình muốn người xem nhớ điều gì nhất?", "Đặt câu hỏi", "Thông tin nào cần biết trước khi thiết kế?", ["Người xem và thông điệp chính", "Màu yêu thích của riêng mình"], ["Hiểu người xem giúp chọn cách thể hiện phù hợp.", "Sở thích cá nhân chưa đủ. Thiết kế cần phục vụ thông điệp và người xem."]),
            scene("10:00", "Phác thảo nhiều khả năng", "sketch", "Trên giấy, An thử ba bố cục khác nhau. Những nét vẽ nhanh giúp cô so sánh cách sắp xếp chữ và hình trước khi làm bản chi tiết.", "Thử thêm một cách nữa xem sao!", "Tư duy hình ảnh", "Vì sao nên phác nhiều phương án?", ["Để chọn và so sánh ý tưởng", "Vì bản đầu tiên luôn sai"], ["Nhiều phương án giúp nhìn ra điểm mạnh của từng cách thể hiện.", "Bản đầu có thể tốt. Phác thêm giúp so sánh, không phải vì mọi bản đầu đều sai."]),
            scene("13:30", "Đưa bản vẽ lên màn hình", "layout", "An chọn màu, hình và kiểu chữ cho poster. Cô kiểm tra tiêu đề, ngày tổ chức và địa điểm có dễ đọc ở kích thước thật không.", "Đẹp rồi, nhưng đã dễ đọc chưa?", "Chú ý chi tiết", "Chữ đẹp nhưng khó đọc. An nên…", ["Giữ nguyên vì trông nghệ thuật", "Điều chỉnh chữ và độ tương phản"], ["Poster cần giúp người xem nhận được thông tin.", "Đúng rồi. Dễ đọc là một phần quan trọng của thiết kế."], 1),
            scene("16:00", "Lắng nghe để hoàn thiện", "review", "Ban tổ chức góp ý rằng thời gian còn quá nhỏ. An sửa lại, kiểm tra thông tin và xuất tệp phù hợp để in.", "Góp ý giúp câu chuyện rõ hơn.", "Hợp tác & chỉnh sửa", "Khi nhận góp ý, điều gì nên làm?", ["Hỏi rõ mục tiêu rồi điều chỉnh", "Bỏ hết ý tưởng mà không trao đổi"], ["Hiểu lý do của góp ý giúp chỉnh sửa có chủ đích.", "Hãy trao đổi để biết điều cần cải thiện trước khi thay đổi toàn bộ."]),
        ],
    },
    "giao-vien": {
        "character": "Cô giáo Mai", "intro": "Một lớp học, nhiều cách hiểu, và những khoảnh khắc “à, ra thế!”.",
        "takeaway": "Giáo viên không chỉ giảng bài. Quan sát, chuẩn bị hoạt động và hỗ trợ cách học khác nhau là những phần quan trọng của nghề.",
        "source": "education-training-and-library/high-school-teachers.htm",
        "scenes": [
            scene("07:00", "Chuẩn bị điều thú vị", "lesson", "Mai chuẩn bị bài học về cây xanh. Cô chọn một câu hỏi mở và những chiếc lá quen thuộc để học sinh có thể quan sát.", "Làm sao để cả lớp cùng muốn tìm hiểu?", "Tổ chức & sáng tạo", "Hoạt động mở đầu nên giúp học sinh…", ["Tò mò và kết nối với bài học", "Nhớ ngay mọi đáp án"], ["Sự tò mò tạo một điểm bắt đầu để khám phá.", "Hiểu bài cần thời gian. Hoạt động mở đầu có thể khơi gợi câu hỏi trước."]),
            scene("08:00", "Cùng khám phá trong lớp", "classroom", "Học sinh chia nhóm quan sát lá. Mai đi quanh lớp, lắng nghe câu hỏi và gợi ý để các nhóm tự tìm ra điểm khác nhau.", "Em nhận thấy điều gì? Kể cô nghe nhé.", "Giao tiếp & hướng dẫn", "Một nhóm đang bí. Cô có thể…", ["Đưa một câu hỏi gợi mở", "Làm thay toàn bộ hoạt động"], ["Gợi mở giúp học sinh tiếp tục tự khám phá.", "Làm thay sẽ làm mất cơ hội thử. Một gợi ý vừa đủ có thể hữu ích hơn."]),
            scene("11:00", "Nhìn ra từng bước tiến", "marking", "Mai đọc bài làm và ghi nhận xét cụ thể: điều học sinh làm tốt và một điểm có thể thử lại. Cô điều chỉnh bài học sau từ những quan sát đó.", "Ý này tốt rồi, mình thử giải thích rõ hơn nhé.", "Quan sát & phản hồi", "Nhận xét nào giúp người học tiến bộ?", ["Một lời chê chung chung", "Chỉ rõ điểm tốt và cách cải thiện"], ["Nhận xét chung chung khó giúp người học biết phải làm gì tiếp.", "Đúng rồi. Phản hồi cụ thể tạo ra bước tiếp theo có thể thực hiện."], 1),
            scene("15:00", "Tìm cách học phù hợp", "mentoring", "Một học sinh còn chưa hiểu bài. Mai thử dùng tranh và ví dụ khác, rồi trao đổi cùng đồng nghiệp để tìm thêm cách hỗ trợ.", "Mình thử một cách giải thích khác nhé.", "Kiên nhẫn & đồng cảm", "Khi học sinh chưa hiểu, Mai nên…", ["Thử cách giải thích khác", "Cho rằng bạn ấy không thể học"], ["Mỗi người có thể cần cách hỗ trợ khác nhau.", "Chưa hiểu một bài không nói lên khả năng lâu dài. Cần tìm cách hỗ trợ phù hợp."]),
        ],
    },
    "ky-su-moi-truong": {
        "character": "Kỹ sư Hà", "intro": "Theo dấu một dòng nước, từ dữ liệu đến giải pháp cho môi trường.",
        "takeaway": "Kỹ sư môi trường kết hợp làm việc hiện trường, phân tích dữ liệu và thiết kế giải pháp. Kết quả cần được đo lường, không chỉ nhìn bằng mắt.",
        "source": "architecture-and-engineering/environmental-engineers.htm",
        "scenes": [
            scene("08:00", "Quan sát tại hiện trường", "sampling", "Hà cùng nhóm đến điểm lấy mẫu theo kế hoạch. Mọi người dùng dụng cụ phù hợp, ghi vị trí và thời gian để dữ liệu có thể đối chiếu.", "Mỗi mẫu đều cần một ghi chép rõ ràng.", "Cẩn thận & kỷ luật", "Vì sao phải ghi nhãn mẫu?", ["Để biết mẫu đến từ đâu và lúc nào", "Chỉ để lọ trông chuyên nghiệp"], ["Thông tin đi kèm giúp việc phân tích và so sánh có ý nghĩa.", "Nhãn chứa thông tin cần thiết để tránh nhầm mẫu."]),
            scene("10:30", "Đọc điều dữ liệu kể", "analysis", "Về nơi làm việc, Hà xem kết quả phân tích và so sánh giữa các lần đo. Một điểm bất thường khiến cô kiểm tra lại dữ liệu trước khi kết luận.", "Mình kiểm tra lại điểm khác biệt này nhé.", "Phân tích & kiểm chứng", "Thấy một số đo khác thường, nên…", ["Kết luận ngay có vấn đề lớn", "Kiểm tra cách đo và dữ liệu liên quan"], ["Một số đo cần được xem trong bối cảnh và kiểm chứng.", "Đúng rồi. Kiểm tra giúp tránh kết luận vội."], 1),
            scene("14:00", "Phác một giải pháp xanh", "system", "Nhóm của Hà xem sơ đồ hệ thống xử lý nước. Họ so sánh những cách cải thiện hiệu quả, nhu cầu năng lượng và khả năng vận hành.", "Giải pháp cần hiệu quả và dùng được trong thực tế.", "Tư duy hệ thống", "Khi chọn giải pháp, cần xem xét…", ["Hiệu quả, nguồn lực và vận hành", "Chỉ hình thức của bản vẽ"], ["Một giải pháp cần phù hợp cả mục tiêu lẫn điều kiện thực hiện.", "Bản vẽ giúp trình bày, nhưng hiệu quả thực tế mới cần được kiểm chứng."]),
            scene("16:00", "Theo dõi để cải thiện", "monitoring", "Hà trao đổi với người vận hành và theo dõi kết quả sau điều chỉnh. Cô viết báo cáo rõ ràng về điều đã cải thiện và điều cần kiểm tra thêm.", "Cùng đo lại để biết thay đổi có hiệu quả không.", "Trách nhiệm & hợp tác", "Sau khi điều chỉnh hệ thống, cần…", ["Theo dõi số liệu và phản hồi", "Xem như đã xong mãi mãi"], ["Theo dõi giúp biết giải pháp có hoạt động ổn định không.", "Điều kiện có thể thay đổi, nên vẫn cần kiểm tra và cải thiện."]),
        ],
    },
    "truyen-thong": {
        "character": "Người làm truyền thông Vy", "intro": "Đi tìm một câu chuyện thật và cách kể để mọi người muốn lắng nghe.",
        "takeaway": "Truyền thông cần viết tốt, biết lắng nghe và kiểm tra thông tin. Một nội dung hữu ích bắt đầu từ sự tôn trọng người trong câu chuyện.",
        "source": "media-and-communication/public-relations-specialists.htm",
        "scenes": [
            scene("09:00", "Chọn câu chuyện đáng kể", "editorial", "Vy chuẩn bị bài về một hoạt động đổi sách. Cô xác định người đọc và lên danh sách những thông tin cần tìm hiểu.", "Câu chuyện này có ích cho ai?", "Lập kế hoạch", "Trước khi viết, nên xác định…", ["Người đọc và mục đích bài viết", "Số lượt thích chắc chắn sẽ có"], ["Mục tiêu rõ giúp chọn nội dung phù hợp.", "Không thể biết chắc lượt thích. Hãy bắt đầu từ người đọc và thông tin hữu ích."]),
            scene("10:30", "Lắng nghe người trong cuộc", "interview", "Vy xin phép phỏng vấn một bạn tham gia. Cô ghi lại ý chính và hỏi rõ những chi tiết còn chưa chắc chắn.", "Mình có thể dùng lời chia sẻ này trong bài không?", "Lắng nghe & tôn trọng", "Trước khi dùng ảnh của người khác, nên…", ["Xin phép và nói rõ mục đích", "Đăng ngay vì ảnh rất đẹp"], ["Xin phép thể hiện sự tôn trọng người xuất hiện trong nội dung.", "Ảnh đẹp vẫn cần được sử dụng với sự đồng ý phù hợp."]),
            scene("14:00", "Viết, kiểm tra, rồi biên tập", "editing", "Vy chọn tiêu đề rõ ràng, kiểm tra tên sự kiện và thời gian. Một đồng nghiệp đọc lại để phát hiện chỗ dễ gây hiểu nhầm.", "Thông tin đã đúng và dễ hiểu chưa?", "Viết & kiểm chứng", "Một chi tiết chưa có nguồn rõ, Vy nên…", ["Đăng trước rồi sửa sau", "Xác minh trước khi sử dụng"], ["Thông tin sai có thể gây hiểu nhầm dù sau đó được sửa.", "Đúng rồi. Kiểm tra nguồn là một phần trách nhiệm khi kể chuyện."], 1),
            scene("16:30", "Nghe phản hồi sau khi đăng", "feedback", "Sau khi bài được duyệt và đăng, Vy đọc câu hỏi của người xem. Cô tổng hợp phản hồi và ghi lại điều cần làm rõ cho nội dung sau.", "Mọi người còn muốn biết điều gì nữa nhỉ?", "Đồng cảm & điều chỉnh", "Bình luận góp ý có thể giúp Vy…", ["Hiểu điều người đọc còn băn khoăn", "Chỉ đếm ai đồng ý với mình"], ["Phản hồi giúp tìm chủ đề và cải thiện cách giải thích.", "Ý kiến khác nhau cũng có thể chứa thông tin hữu ích."]),
        ],
    },
}


def get_story(career_id):
    if career_id not in STORIES:
        return None
    career = next(c for c in CAREERS if c["id"] == career_id)
    story = STORIES[career_id]
    return {**career, **story, "source_url": "https://www.bls.gov/ooh/" + story["source"],
            "source_label": "Tham khảo nhiệm vụ nghề: BLS Occupational Outlook Handbook",
            "note": "Câu chuyện và nhân vật hư cấu do La Bàn biên soạn. Giờ làm minh họa; công việc thay đổi theo vị trí và nơi làm việc. Nguồn tham khảo mô tả nghề tại Hoa Kỳ, không dùng làm lộ trình đào tạo tại Việt Nam."}
