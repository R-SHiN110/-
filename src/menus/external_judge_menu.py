from datetime import datetime, date
from src.utils.file_io import read_json, write_json
from src.utils.helpers import display_menu


DEFENSE_REQUESTS_FILE = "data/requests/defense_requests.json"
DEFENDED_THESES_FILE = "data/theses/defended_theses.json"


def external_judge_menu(user):
    """نمایش منوی اصلی داور"""
    while True:
        menu_title = f"منوی استاد - {user.name}"
        options = [
            "نمره دهی جلسات دفاع شده",
            "تغییر رمز عبور",
            "خروج از حساب کاربری"
        ]

        display_menu(menu_title, options)

        choice = input("لطفاً گزینه مورد نظر را انتخاب کنید: ").strip()

        if choice == "1":
            grade_theses_as_external(user)
        elif choice == "2":
            change_password(user)
        elif choice == "3":
            print("خروج از حساب کاربری...")
            break
        else:
            print("⚠️  گزینه نامعتبر!")
            input("برای ادامه Enter بزنید...")


def grade_theses_as_external(user):
    """نمره‌دهی پایان‌نامه‌ها توسط داور خارجی"""
    print("\n📊 نمره‌دهی جلسات دفاع شده")
    print("=" * 50)

    defense_requests = read_json(DEFENSE_REQUESTS_FILE)
    today = date.today()

    # پایان‌نامه‌هایی که این کاربر داور خارجی آن‌هاست و هنوز نمره نداده
    theses_for_judge = [
        th for th in defense_requests
        if th.get("external_judge_id") == user.user_id and "external_grade" not in th
    ]

    if not theses_for_judge:
        print("📂 پایان‌نامه‌ای برای نمره‌دهی یافت نشد.")
        input("برای ادامه Enter بزنید...")
        return

    students = read_json("data/users/students.json")
    students_dict = {s["user_id"]: s for s in students} if students else {}

    print("\n📚 لیست پایان‌نامه‌های در انتظار نمره‌دهی (داور خارجی):")
    for idx, thesis in enumerate(theses_for_judge, start=1):
        student_info = students_dict.get(thesis["student_id"], {})
        student_name = student_info.get("name", "نامشخص")

        print(f"\n{idx}. 👨‍🎓 دانشجو: {student_name}")
        print(f"   🔢 کد دانشجو: {thesis['student_id']}")
        print(f"   📚 عنوان: {thesis.get('title', 'نامشخص')}")
        print(f"   📅 تاریخ دفاع: {thesis.get('defense_date', 'نامشخص')}")
        print("-" * 40)

    try:
        choice = int(input("شماره پایان‌نامه را انتخاب کنید: ").strip())
        if choice < 1 or choice > len(theses_for_judge):
            print("⚠️ انتخاب نامعتبر!")
            input("برای ادامه Enter بزنید...")
            return
    except ValueError:
        print("⚠️ لطفاً یک عدد وارد کنید.")
        input("برای ادامه Enter بزنید...")
        return

    thesis = theses_for_judge[choice - 1]

    # گرفتن نمره
    try:
        grade = float(input("نمره داور خارجی را وارد کنید (0 تا 20): ").strip())
        if grade < 0 or grade > 20:
            print("⚠️ نمره باید بین 0 و 20 باشد.")
            input("برای ادامه Enter بزنید...")
            return
    except ValueError:
        print("⚠️ نمره نامعتبر!")
        input("برای ادامه Enter بزنید...")
        return

    # ثبت نمره و تاریخ آن
    for th in defense_requests:
        if th["student_id"] == thesis["student_id"] and th["title"] == thesis["title"]:
            th["external_grade"] = grade
            th["external_grade_date"] = today.strftime("%Y-%m-%d")
            print("✅ نمره داور خارجی ثبت شد.")

            # اگر internal_grade_date هم موجود بود، نمره نهایی محاسبه شود
            if "internal_grade" in th and "internal_grade_date" in th:
                internal_grade = th["internal_grade"]
                external_grade = th["external_grade"]
                final_grade = (internal_grade + external_grade) / 2

                # محاسبه نمره حروفی
                if final_grade >= 17:
                    final_letter = "الف"
                elif final_grade >= 14:
                    final_letter = "ب"
                elif final_grade >= 10:
                    final_letter = "ج"
                else:
                    final_letter = "د"

                th["final_grade"] = final_grade
                th["final_letter_grade"] = final_letter
                th["status"] = "مختومه"

                print(f"🎯 نمره نهایی: {final_grade:.2f} ({final_letter})")

                # انتقال به defended_theses.json
                defended = read_json(DEFENDED_THESES_FILE)
                defended.append(th.copy())
                write_json(DEFENDED_THESES_FILE, defended)

                print("📂 پایان‌نامه به لیست نهایی اضافه شد.")

            break

    # ذخیره تغییرات
    write_json(DEFENSE_REQUESTS_FILE, defense_requests)

    # افزایش ظرفیت داور خارجی پس از نمره‌دهی
    external_judges = read_json("data/users/external_judges.json")
    for judge in external_judges:
        if judge["user_id"] == user.user_id:
            judge["judge_capacity"] = judge.get("judge_capacity", 0) + 1
            print(f"✅ ظرفیت داوری شما به {judge['judge_capacity']} افزایش یافت.")
            break

    write_json("data/users/external_judges.json", external_judges)

    input("برای ادامه Enter بزنید...")


def change_password(user):
    """تغییر رمز عبور"""
    print("\n🔒 تغییر رمز عبور")
    print("-" * 40)

    old_password = input("رمز عبور فعلی: ")
    new_password = input("رمز عبور جدید: ")
    confirm_password = input("تکرار رمز عبور جدید: ")

    # استفاده از تابع change_password از auth.py
    from src.utils.auth import change_password as auth_change_password
    auth_change_password(user, old_password, new_password, confirm_password)

    input("\nبرای بازگشت Enter بزنید...")