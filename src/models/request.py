from datetime import datetime


class EnrollmentRequest:
    """
    کلاس درخواست اخذ پایان‌نامه
    """
    STATUS_PENDING = "در انتظار تأیید استاد"
    STATUS_APPROVED = "تأیید شده"
    STATUS_REJECTED = "رد شده"

    def __init__(self, request_id: str, student_id: str, course_id: str, professor_id: str, status: str = STATUS_PENDING):
        self.request_id = request_id
        self.student_id = student_id
        self.course_id = course_id
        self.professor_id = professor_id
        self.status = status
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # تاریخ ایجاد

    def to_dict(self) -> dict:
        """تبدیل شیء درخواست به دیکشنری برای ذخیره در JSON"""
        return {
            "request_id": self.request_id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "professor_id": self.professor_id,
            "status": self.status,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """ساخت یک شیء EnrollmentRequest از یک دیکشنری"""
        request = cls(
            data["request_id"],
            data["student_id"],
            data["course_id"],
            data["professor_id"],
            data["status"]
        )
        request.created_at = data["created_at"]
        return request