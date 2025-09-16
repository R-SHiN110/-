class ThesisCourse:
    """
    کلاس درس پایان‌نامه
    """
    def __init__(self, course_id: str, title: str, professor_id: str, year: int, semester: str, capacity: int, resources: str, sessions_count: int, units: int):
        self.course_id = course_id  # پوئیک
        self.title = title
        self.professor_id = professor_id  # کد استاد مربوطه
        self.year = year  # مثال: 1403
        self.semester = semester  # "نیمسال اول" یا "نیمسال دوم"
        self.capacity = capacity
        self.resources = resources  # منابع درس
        self.sessions_count = sessions_count
        self.units = units

    def to_dict(self) -> dict:
        """تبدیل شیء درس به دیکشنری برای ذخیره در JSON"""
        return {
            "course_id": self.course_id,
            "title": self.title,
            "professor_id": self.professor_id,
            "year": self.year,
            "semester": self.semester,
            "capacity": self.capacity,
            "resources": self.resources,
            "sessions_count": self.sessions_count,
            "units": self.units
        }

    @classmethod
    def from_dict(cls, data: dict):
        """ساخت یک شیء ThesisCourse از یک دیکشنری"""
        return cls(
            data["course_id"],
            data["title"],
            data["professor_id"],
            data["year"],
            data["semester"],
            data["capacity"],
            data["resources"],
            data["sessions_count"],
            data["units"]
        )