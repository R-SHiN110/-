class Thesis:
    """
    کلاس پایان‌نامه
    """
    def __init__(self, thesis_id: str, title: str, abstract: str, keywords: list, student_id: str, supervisor_id: str, file_path: str, image_path: str, defense_date: str, internal_judge_id: str, external_judge_id: str, score: str = None):
        self.thesis_id = thesis_id
        self.title = title
        self.abstract = abstract
        self.keywords = keywords
        self.student_id = student_id
        self.supervisor_id = supervisor_id
        self.file_path = file_path  # مسیر فایل PDF
        self.image_path = image_path  # مسیر تصویر صفحه اول و آخر
        self.defense_date = defense_date
        self.internal_judge_id = internal_judge_id  # کد داور داخلی
        self.external_judge_id = external_judge_id  # کد داور خارجی
        self.score = score  # نمره: الف، ب، ج، د
        self.attendees = []  # لیست حاضرین در جلسه
        self.result = None  # نتیجه دفاع: "دفاع" یا "دفاع مجدد"

    def to_dict(self) -> dict:
        """تبدیل شیء پایان‌نامه به دیکشنری برای ذخیره در JSON"""
        return {
            "thesis_id": self.thesis_id,
            "title": self.title,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "student_id": self.student_id,
            "supervisor_id": self.supervisor_id,
            "file_path": self.file_path,
            "image_path": self.image_path,
            "defense_date": self.defense_date,
            "internal_judge_id": self.internal_judge_id,
            "external_judge_id": self.external_judge_id,
            "score": self.score,
            "attendees": self.attendees,
            "result": self.result
        }

    @classmethod
    def from_dict(cls, data: dict):
        """ساخت یک شیء Thesis از یک دیکشنری"""
        thesis = cls(
            data["thesis_id"],
            data["title"],
            data["abstract"],
            data["keywords"],
            data["student_id"],
            data["supervisor_id"],
            data["file_path"],
            data["image_path"],
            data["defense_date"],
            data["internal_judge_id"],
            data["external_judge_id"],
            data["score"]
        )
        thesis.attendees = data["attendees"]
        thesis.result = data["result"]
        return thesis