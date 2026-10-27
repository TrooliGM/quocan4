import unittest
from pydantic import ValidationError
from career_library import Career, Catalog, CATEGORIES, normalize_search


def sample():
    return dict(career_id='lap-trinh', name='Lập trình viên', category_id='technology',
        short_description='Viết và kiểm tra phần mềm.', description='Xây dựng ứng dụng để giải quyết nhu cầu của người dùng.',
        daily_tasks=['Viết mã', 'Kiểm tra lỗi'], skills=['Tư duy logic', 'Làm việc nhóm'],
        related_subjects=['Tin học'], work_environment='Làm việc trong nhóm phát triển phần mềm.',
        challenges=['Yêu cầu thay đổi trong quá trình phát triển'], keywords=['máy tính', 'ứng dụng'])


class CareerContractTests(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(len(CATEGORIES),12)

    def test_existing_id_is_stable(self):
        self.assertEqual(Career(**sample()).career_id,'lap-trinh')

    def test_accent_case_and_keywords(self):
        catalog=Catalog(careers=[Career(**sample())])
        for q in ('LẬP TRÌNH','lap trinh','may tinh','cong nghe'):
            self.assertEqual(len(catalog.search(q)),1)
        self.assertEqual(catalog.search('không có nghề này'),[])
        self.assertEqual(catalog.search(category_id='health'),[])
        self.assertEqual(normalize_search(' ĐIỆN ẢNH '),'dien anh')

    def test_validation(self):
        for changes in ({'category_id':'invalid'},{'career_id':'../path'},{'skills':['',' ']}, {'keywords':[]}):
            with self.assertRaises(ValidationError): Career(**{**sample(),**changes})

    def test_duplicate_ids_and_names(self):
        career=Career(**sample())
        with self.assertRaises(ValidationError): Catalog(careers=[career,career])
        with self.assertRaises(ValidationError):
            Catalog(careers=[career,Career(**{**sample(),'career_id':'other','name':'LẬP TRÌNH VIÊN'})])
