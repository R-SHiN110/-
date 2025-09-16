import hashlib
from typing import Optional, Dict, Any
from src.models.user import Student, Professor, User, external_judge
from src.utils.file_io import read_json, write_json


def hash_password(password: str) -> str:
    """
    هش کردن رمز عبور با الگوریتم SHA-256
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def change_password(user: User, old_password: str, new_password: str, confirm_password: str) -> bool:
    """
    تغییر رمز عبور کاربر
    بازگشت: True در صورت موفقیت، False در صورت شکست
    """
    try:
        # تعیین مسیر فایل بر اساس نقش کاربر
        role = user.get_role()
        file_path = f"data/users/{role}s.json"

        # خواندن داده کاربران از فایل
        users_data = read_json(file_path)

        if not users_data:
            print("❌ خطا در خواندن اطلاعات کاربران!")
            return False

        # پیدا کردن کاربر فعلی در فایل
        user_data = next((u for u in users_data if u["user_id"] == user.user_id), None)

        if not user_data:
            print("❌ اطلاعات کاربر یافت نشد!")
            return False

        # شرط اول: بررسی صحت رمز عبور فعلی
        hashed_old_password = hash_password(old_password)
        if user_data["password"] != hashed_old_password:
            print("❌ رمز عبور فعلی اشتباه است!")
            return False

        # شرط دوم: بررسی تطابق رمز عبور جدید با تکرار آن
        if new_password != confirm_password:
            print("❌ رمزهای عبور جدید مطابقت ندارند!")
            return False

        # شرط سوم: هش کردن رمز عبور جدید و ذخیره در فایل
        hashed_new_password = hash_password(new_password)

        # آپدیت رمز عبور در داده‌های حافظه
        user_data["password"] = hashed_new_password

        # آپدیت رمز عبور در شیء کاربر فعلی
        user._password = hashed_new_password

        # ذخیره تغییرات در فایل
        if write_json(file_path, users_data):
            print("✅ رمز عبور با موفقیت تغییر یافت.")
            return True
        else:
            print("❌ خطا در ذخیره‌سازی تغییرات!")
            return False

    except Exception as e:
        print(f"❌ خطای ناشناخته: {e}")
        return False


def verify_user(user_id: str, password: str, role: str) -> Optional[User]:
    """
    بررسی صحت credentials کاربر و برگرداندن شیء User در صورت موفقیت
    """
    try:
        # انتخاب فایل مناسب بر اساس نقش کاربر
        if role == "student":
            file_path = "data/users/students.json"

        elif role == "professor":
            file_path = "data/users/professors.json"

        else:
            file_path = "data/users/external_judges.json"

        # خواندن داده کاربران از فایل
        users_data = read_json(file_path)

        # جستجوی کاربر با user_id مشخص
        user_data = next((u for u in users_data if u["user_id"] == user_id), None)

        if user_data:
            # بررسی تطابق رمز عبور (هش شده)
            hashed_input_password = hash_password(password)
            if user_data["password"] == hashed_input_password:
                # ایجاد شیء User مناسب
                if role == "student":
                    return Student(
                        user_data["user_id"],
                        user_data["national_id"],
                        user_data["name"],
                        user_data["password"]
                    )
                elif role == "professor":
                    return Professor(
                        user_data["user_id"],
                        user_data["national_id"],
                        user_data["name"],
                        user_data["password"]
                    )
                else:
                    return external_judge(
                        user_data["user_id"],
                        user_data["national_id"],
                        user_data["name"],
                        user_data["password"]
                    )
        return None
    except Exception as e:
        print(f"خطا در بررسی کاربر: {e}")
        return None


def find_user_by_id(user_id: str, role: str) -> Optional[Dict[str, Any]]:
    """
    پیدا کردن کاربر بر اساس ID و نقش
    بازگشت: دیکشنری داده کاربر یا None
    """
    try:
        file_path = "data/users/students.json" if role == "student" else "data/users/professors.json"
        users_data = read_json(file_path)
        return next((u for u in users_data if u["user_id"] == user_id), None)
    except Exception as e:
        print(f"خطا در یافتن کاربر: {e}")
        return None


def get_user_name(user_id: str, role: str) -> str:
    """
    پیدا کردن نام کاربر بر اساس ID و نقش
    بازگشت: نام کاربر یا 'نامشخص'
    """
    user_data = find_user_by_id(user_id, role)
    return user_data.get("name", "نامشخص") if user_data else "نامشخص"


def get_all_professors() -> list:
    """
    دریافت لیست همه اساتید
    بازگشت: لیستی از دیکشنری‌های اطلاعات اساتید
    """
    try:
        return read_json("data/users/professors.json")
    except Exception as e:
        print(f"خطا در دریافت لیست اساتید: {e}")
        return []


def get_all_students() -> list:
    """
    دریافت لیست همه دانشجویان
    بازگشت: لیستی از دیکشنری‌های اطلاعات دانشجویان
    """
    try:
        return read_json("data/users/students.json")
    except Exception as e:
        print(f"خطا در دریافت لیست دانشجویان: {e}")
        return []
