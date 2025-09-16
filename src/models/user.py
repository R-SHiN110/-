import json
from datetime import datetime
from abc import ABC, abstractmethod

class User(ABC):
    """
    کلاس انتزاعی پایه برای همه کاربران سیستم
    """
    def __init__(self, user_id: str, national_id: str, name: str, password: str):
        self.user_id = user_id  # کد دانشجویی یا کد استادی
        self.national_id = national_id
        self.name = name
        self._password = password  # پسورد به صورت هش شده ذخیره خواهد شد

    @abstractmethod
    def get_role(self) -> str:
        """نقش کاربر را برمی‌گرداند (پیاده‌سازی در کلاس‌های فرزند)"""
        pass

    def to_dict(self) -> dict:
        """تبدیل شیء کاربر به دیکشنری برای ذخیره در JSON"""
        return {
            "user_id": self.user_id,
            "national_id": self.national_id,
            "name": self.name,
            "password": self._password,  # در واقعیت باید فقط هش ذخیره شود
            "role": self.get_role()
        }

class Student(User):
    """
    کلاس دانشجو
    """
    def get_role(self) -> str:
        return "student"

class external_judge(User):
    """
    کلاس داور خارجی
    """
    def get_role(self) -> str:
        return "external_judge"


class Professor(User):
    """
    کلاس استاد
    """
    def __init__(self, user_id: str, national_id: str, name: str, password: str):
        super().__init__(user_id, national_id, name, password)
        self._supervision_capacity = 5  # ظرفیت راهنمایی: ۵ دانشجو
        self._judgment_capacity = 10    # ظرفیت داوری: ۱۰ دانشجو

    def get_role(self) -> str:
        return "professor"

    def has_supervision_capacity(self) -> bool:
        """آیا استاد ظرفیت خالی برای راهنمایی دارد؟"""
        # TODO: باید تعداد دانشجویان تحت راهنمایی این استاد از فایل JSON شمارش شود
        # فعلاً به صورت ساده:
        return self._supervision_capacity > 0

    def has_judgment_capacity(self) -> bool:
        """آیا استاد ظرفیت خالی برای داوری دارد؟"""
        # TODO: باید تعداد داوری‌های فعال این استاد از فایل JSON شمارش شود
        # فعلاً به صورت ساده:
        return self._judgment_capacity > 0