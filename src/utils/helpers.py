from datetime import datetime, timedelta
import re
from src.utils.file_io import read_json, write_json

def validate_email(email: str) -> bool:
    """
    بررسی صحت فرمت ایمیل
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    بررسی صحت فرمت شماره تلفن ایرانی
    """
    pattern = r'^09[0-9]{9}$'
    return re.match(pattern, phone) is not None


def is_valid_date(date_string: str, date_format: str = "%Y-%m-%d") -> bool:
    """
    بررسی معتبر بودن تاریخ
    """
    try:
        datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False


def is_three_months_passed(start_date: str, date_format: str = "%Y-%m-%d") -> bool:
    """
    بررسی اینکه آیا ۳ ماه از تاریخ داده شده گذشته است یا خیر
    """
    try:
        start = datetime.strptime(start_date, date_format)
        three_months_later = start + timedelta(days=90)  # تقریباً ۳ ماه
        return datetime.now() >= three_months_later
    except ValueError:
        return False


def format_date(date_string: str, input_format: str = "%Y-%m-%d", output_format: str = "%Y/%m/%d") -> str:
    """
    قالب‌بندی مجدد تاریخ
    """
    try:
        date_obj = datetime.strptime(date_string, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return date_string


def display_menu(menu_title: str, options: list) -> None:
    """
    نمایش یک منوی زیبا در کنسول
    """
    # print(f"\n{'-' * 50}")
    # print(f" {menu_title} ")
    # print(f"{'-' * 50}")
    #
    # for i, option in enumerate(options, 1):
    #     print(f" {i}. {option}")
    #
    # print(f"{'-' * 50}")
    print(f"\n{'=' * 50}\n{menu_title}\n{'=' * 50}")
    for idx, option in enumerate(options, start=1):
        print(f"{idx}. {option}")
    print("-" * 50)


def get_semester_year(defense_date: str, date_format: str = "%Y-%m-%d") -> str:
    """
    محاسبه سال-نیمسال بر اساس تاریخ دفاع پایان نامه

    defense_date: تاریخ دفاع به فرمت مشخص شده (پیش‌فرض: YYYY-MM-DD)
    خروجی: رشته‌ای شامل سال و نیمسال
    """
    date_obj = datetime.strptime(defense_date, date_format)
    year = date_obj.year
    month = date_obj.month

    if 1 <= month <= 6:
        # نیمسال دوم
        return f"{year - 1}-{year} (نیمسال دوم)"
    else:
        # نیمسال اول
        return f"{year}-{year + 1} (نیمسال اول)"


def search_theses(search_query: str, search_type: str):
    """
    جستجو در پایان‌نامه‌های مختومه
    """
    try:
        # خواندن پایان‌نامه‌های مختومه
        theses = read_json("data/theses/defended_theses.json")

        if not theses:
            return []

        # نرمالایز کردن query
        search_query = search_query.strip().lower()

        results = []

        for thesis in theses:
            # جستجو بر اساس نوع
            if search_type == "title" and search_query in thesis.get("title", "").lower():
                results.append(thesis)

            elif search_type == "professor":
                # جستجو بر اساس استاد راهنما
                prof_id = thesis.get("professor_id", "")
                professors = read_json("data/users/professors.json")
                professor = next((p for p in professors if p["user_id"] == prof_id), {})
                if search_query in professor.get("name", "").lower():
                    results.append(thesis)

            elif search_type == "keywords":
                # جستجو در کلمات کلیدی
                keywords = thesis.get("keywords", [])
                if any(search_query in keyword.lower() for keyword in keywords):
                    results.append(thesis)

            elif search_type == "author":
                # جستجو بر اساس نویسنده (دانشجو)
                student_id = thesis.get("student_id", "")
                students = read_json("data/users/students.json")
                student = next((s for s in students if s["user_id"] == student_id), {})
                if search_query in student.get("name", "").lower():
                    results.append(thesis)

            elif search_type == "year":
                # جستجو بر اساس سال دفاع
                defense_date = thesis.get("defense_date", "")
                if defense_date.startswith(search_query):
                    results.append(thesis)

            elif search_type == "judges":
                # جستجو بر اساس داوران
                internal_judge_id = thesis.get("internal_judge_id", "")
                external_judge_id = thesis.get("external_judge_id", "")

                # خواندن اطلاعات داوران
                professors = read_json("data/users/professors.json")
                external_judges = read_json("data/users/external_judges.json")

                # بررسی داور داخلی
                internal_judge = next((p for p in professors if p["user_id"] == internal_judge_id), {})
                external_judge = next((j for j in external_judges if j["user_id"] == external_judge_id), {})

                if (search_query in internal_judge.get("name", "").lower() or
                        search_query in external_judge.get("name", "").lower()):
                    results.append(thesis)

        return results

    except Exception as e:
        print(f"خطا در جستجو: {e}")
        return []


def open_file(file_path):
    """باز کردن فایل با برنامه پیشفرض سیستم"""
    import os
    import subprocess
    import sys
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS, Linux
            if sys.platform == 'darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux
                subprocess.call(('xdg-open', file_path))
        return True
    except Exception as e:
        print(f"❌ خطا در باز کردن فایل: {e}")
        return False