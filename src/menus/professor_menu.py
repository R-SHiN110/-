import sys
import os
import subprocess
from src.utils.file_io import read_json, write_json, get_full_path
from src.utils.helpers import display_menu
from datetime import datetime, date


def get_available_internal_judges(exclude_professor_id=None):
    """دریافت لیست اساتید با ظرفیت داوری بجز استاد راهنما"""
    professors = read_json("data/users/professors.json")

    available_judges = [
        p for p in professors
        if p.get("judge_capacity", 0) > 0
           and p["user_id"] != exclude_professor_id
    ]
    return available_judges


def get_available_external_judges():
    """دریافت لیست داوران خارجی با ظرفیت موجود"""
    external_judges = read_json("data/users/external_judges.json")
    available_judges = [j for j in external_judges if j.get("judge_capacity", 0) > 0]
    return available_judges


def decrease_judge_capacity(judge_id, is_external=False):
    """کاهش ظرفیت داوری یک استاد یا داور خارجی"""
    try:
        if is_external:
            file_path = "data/users/external_judges.json"
            judges = read_json(file_path)
        else:
            file_path = "data/users/professors.json"
            judges = read_json(file_path)

        for judge in judges:
            if judge["user_id"] == judge_id and judge.get("judge_capacity", 0) > 0:
                judge["judge_capacity"] -= 1
                break

        write_json(file_path, judges)
        return True
    except Exception as e:
        print(f"خطا در کاهش ظرفیت داور: {e}")
        return False


def open_file(file_path):
    """باز کردن فایل با برنامه پیشفرض سیستم"""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS, Linux
            if sys.platform == 'darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux
                subprocess.call(('xdg-open', file_path))
        print(f"✅ فایل باز شد: {file_path}")
    except Exception as e:
        print(f"❌ خطا در باز کردن فایل: {e}")


def show_professor_menu(professor):
    """نمایش منوی اصلی استاد"""
    while True:
        menu_title = f"منوی استاد - {professor.name}"
        options = [
            "مشاهده و بررسی درخواست‌های اخذ پایان‌نامه",
            "مدیریت درخواست‌های دفاع",
            "نمره دهی جلسات دفاع شده",
            "جستجو در بانک پایان‌نامه‌ها",
            "تغییر رمز عبور",
            "خروج از حساب کاربری"
        ]

        display_menu(menu_title, options)

        choice = input("لطفاً گزینه مورد نظر را انتخاب کنید: ").strip()

        if choice == "1":
            review_enrollment_requests(professor)
        elif choice == "2":
            manage_defense_requests(professor)
        elif choice == "3":
            grade_defense_sessions(professor)
        elif choice == "4":
            search_theses()
        elif choice == "5":
            change_password(professor)
        elif choice == "6":
            print("خروج از حساب کاربری...")
            break
        else:
            print("⚠️  گزینه نامعتبر!")
            input("برای ادامه Enter بزنید...")


def review_enrollment_requests(professor):
    """بررسی درخواست‌های اخذ پایان‌نامه"""
    print("\n📋 درخواست‌های اخذ پایان‌نامه")
    print("-" * 40)

    requests = read_json("data/requests/enrollment_requests.json")
    professor_requests = [r for r in requests if
                          r["professor_id"] == professor.user_id and r["status"] == "در انتظار تأیید استاد"]

    if not professor_requests:
        print("❌ هیچ درخواست pending ندارید.")
        input("برای بازگشت Enter بزنید...")
        return

    # خواندن اطلاعات دانشجویان
    students = read_json("data/users/students.json")
    students_dict = {s["user_id"]: s for s in students} if students else {}

    # خواندن اطلاعات دروس
    courses = read_json("data/courses/thesis_courses.json")
    courses_dict = {c["course_id"]: c for c in courses} if courses else {}

    print(f"\n📝 لیست درخواست‌های اخذ درس پایان نامه برای شما:")
    print("=" * 60)

    for i, req in enumerate(professor_requests, 1):
        student_info = students_dict.get(req["student_id"], {})
        student_name = student_info.get("name", "نامشخص")
        student_id = req["student_id"]
        course_id = req["course_id"]
        request_date = req.get("created_at", "تاریخ نامشخص")

        print(f"\n{i}. 👨‍🎓 دانشجو: {student_name}")
        print(f"   🔢 کد دانشجو: {student_id}")
        print(f"   📅 تاریخ درخواست: {request_date}")
        print("-" * 40)

    try:
        choice = int(input("\nشماره درخواست برای بررسی: ")) - 1
        selected_request = professor_requests[choice]

        # نمایش اطلاعات کامل درخواست
        student_info = students_dict.get(selected_request["student_id"], {})
        student_name = student_info.get("name", "نامشخص")
        course_info = courses_dict.get(selected_request["course_id"], {})
        course_title = course_info.get("title", "نامشخص")

        print(f"\n 🔍 درخواست دانشجو {selected_request['student_id']} برای درس پایان نامه")
        action = input("تایید (y) یا رد (n)? [y/n]: ").strip().lower()

        if action == 'y':
            selected_request["status"] = "تایید شده"
            selected_request["approved_date"] = date.today().strftime("%Y-%m-%d")  # تاریخ واقعی تایید
            print("✅ درخواست تایید شد.")

        elif action == 'n':
            selected_request["status"] = "رد شده"
            selected_request["rejected_date"] = date.today().strftime("%Y-%m-%d")  # تاریخ رد
            print("❌ درخواست رد شد.")

            for course in courses:
                if course["course_id"] == selected_request["course_id"]:
                    course["capacity"] += 1
                    print(f"✅ ظرفیت درس '{course_title}' به {course['capacity']} افزایش یافت.")
                    break

        else:
            print("⚠️  عمل نامعتبر!")
            return

        # آپدیت فایل درخواست‌ها
        for i, req in enumerate(requests):
            if req["student_id"] == selected_request["student_id"]:
                if req["status"] == "در انتظار تأیید استاد":
                    requests[i] = selected_request
                break

        if write_json("data/requests/enrollment_requests.json", requests):
            if action == 'n':  # فقط اگر درخواست رد شده باشد
                if write_json("data/courses/thesis_courses.json", courses):
                    print("✅ تغییرات ظرفیت درس نیز ذخیره شد.")
                else:
                    print("❌ خطا در ذخیره تغییرات ظرفیت درس!")
        else:
            print("❌ خطا در ذخیره تغییرات درخواست!")

    except (ValueError, IndexError):
        print("❌ انتخاب نامعتبر!")

    input("برای بازگشت Enter بزنید...")


def manage_defense_requests(professor):
    """مدیریت درخواست‌های دفاع ارسالی برای استاد"""
    print("\n📝 مدیریت درخواست‌های دفاع")
    print("=" * 50)

    # خواندن درخواست‌های دفاع
    defense_requests = read_json("data/requests/defense_requests.json")

    # فیلتر کردن درخواست‌های مربوط به این استاد و با وضعیت "در انتظار تأیید استاد"
    professor_defense_requests = [
        r for r in defense_requests
        if r["professor_id"] == professor.user_id
           and r["status"] == "در انتظار تأیید استاد"
    ]

    if not professor_defense_requests:
        print("✅ هیچ درخواست دفاع pending ندارید.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    # خواندن اطلاعات دانشجویان
    students = read_json("data/users/students.json")
    students_dict = {s["user_id"]: s for s in students} if students else {}

    print("\n📋 لیست درخواست‌های دفاع pending:")
    print("=" * 60)

    for i, req in enumerate(professor_defense_requests, 1):
        student_info = students_dict.get(req["student_id"], {})
        student_name = student_info.get("name", "نامشخص")

        print(f"\n{i}. 👨‍🎓 دانشجو: {student_name}")
        print(f"   🔢 کد دانشجو: {req['student_id']}")
        print(f"   📚 عنوان پایان‌نامه: {req.get('title', 'نامشخص')}")
        print(f"   📅 تاریخ ارسال درخواست: {req.get('submission_date', 'نامشخص')}")
        print("-" * 40)

    try:
        choice = int(input("\n🎯 شماره درخواست برای بررسی: ")) - 1

        if choice < 0 or choice >= len(professor_defense_requests):
            print("❌ شماره درخواست نامعتبر است!")
            input("\nبرای بازگشت Enter بزنید...")
            return

        selected_request = professor_defense_requests[choice]

        # نمایش منوی مدیریت درخواست
        while True:
            print(
                f"\n📋 مدیریت درخواست دفاع دانشجو: {students_dict.get(selected_request['student_id'], {}).get('name', 'نامشخص')}")
            print("=" * 50)
            print("1. 📄 باز کردن فایل PDF پایان‌نامه")
            print("2. 🖼️ باز کردن عکس صفحه اول")
            print("3. 🖼️ باز کردن عکس صفحه آخر")
            print("4. ❌ رد درخواست")
            print("5. ✅ قبول درخواست و تعیین تاریخ دفاع")
            print("6. ↩️ بازگشت به منوی قبلی")

            action = input("\nلطفاً گزینه مورد نظر را انتخاب کنید: ").strip()

            if action == "1":
                # باز کردن فایل PDF
                pdf_path = get_full_path(selected_request["file_path"])
                if os.path.exists(pdf_path):
                    open_file(pdf_path)
                else:
                    print("❌ فایل PDF پیدا نشد!")

            elif action == "2":
                # باز کردن عکس صفحه اول
                image_path = get_full_path(selected_request["image_path"][0])
                if os.path.exists(image_path):
                    open_file(image_path)
                else:
                    print("❌ عکس صفحه اول پیدا نشد!")

            elif action == "3":
                # باز کردن عکس صفحه آخر
                image_path = get_full_path(selected_request["image_path"][1])
                if os.path.exists(image_path):
                    open_file(image_path)
                else:
                    print("❌ عکس صفحه آخر پیدا نشد!")

            elif action == "4":
                # رد درخواست
                confirm = input("❓ آیا از رد این درخواست اطمینان دارید؟ (y/n): ").strip().lower()
                if confirm == 'y':
                    selected_request["status"] = "رد شده"
                    selected_request["rejected_date"] = date.today().strftime("%Y-%m-%d")

                    # آپدیت فایل درخواست‌ها
                    for i, req in enumerate(defense_requests):
                        if req["student_id"] == selected_request["student_id"]:
                            defense_requests[i] = selected_request
                            break

                    if write_json("data/requests/defense_requests.json", defense_requests):
                        print("✅ درخواست دفاع رد شد.")
                    else:
                        print("❌ خطا در ذخیره تغییرات!")

                    input("\nبرای ادامه Enter بزنید...")
                    break
                else:
                    print("⚠️ عمل رد درخواست لغو شد.")

            elif action == "5":

                # قبول درخواست و تعیین تاریخ دفاع

                print("\n✅ قبول درخواست دفاع و تعیین جزئیات:")

                print("-" * 40)

                # دریافت تاریخ دفاع

                defense_date = input("تاریخ دفاع (YYYY-MM-DD): ").strip()

                # انتخاب داور داخلی

                # انتخاب داور داخلی
                print("\n👨‍🏫 انتخاب داور داخلی:")
                print("-" * 30)

                # دریافت لیست داوران داخلی (به جز خود استاد راهنما)
                internal_judges = get_available_internal_judges(professor.user_id)

                if not internal_judges:
                    print("❌ هیچ داور داخلی با ظرفیت خالی موجود نیست!")
                    # نمایش پیام توضیحی اگر فقط خود استاد راهنما available باشد
                    all_judges = get_available_internal_judges()  # بدون exclude
                    if all_judges and len(all_judges) == 1 and all_judges[0]["user_id"] == professor.user_id:
                        print("ℹ️  فقط خود شما به عنوان داور available هستید که نمی‌توانید انتخاب شوید.")
                    input("\nبرای ادامه Enter بزنید...")
                    continue

                print("\nلیست داوران داخلی available:")
                for i, judge in enumerate(internal_judges, 1):
                    print(f"{i}. {judge['name']} - ظرفیت: {judge.get('judge_capacity', 0)}")

                # نمایش استاد راهنما به عنوان غیرقابل انتخاب (اختیاری)
                all_judges = get_available_internal_judges()  # بدون exclude
                professor_judge = next((j for j in all_judges if j["user_id"] == professor.user_id), None)
                if professor_judge:
                    print(f"👑 شما (استاد راهنما) - ظرفیت: {professor_judge.get('judge_capacity', 0)} - غیرقابل انتخاب")

                try:
                    choice = int(input("\nشماره داور داخلی را انتخاب کنید: ")) - 1
                    if choice < 0 or choice >= len(internal_judges):
                        print("❌ انتخاب نامعتبر!")
                        continue

                    internal_judge = internal_judges[choice]["user_id"]
                    internal_judge_name = internal_judges[choice]["name"]
                    print(f"✅ داور داخلی انتخاب شد: {internal_judge_name}")

                except (ValueError, IndexError):
                    print("❌ انتخاب نامعتبر!")
                    continue

                # انتخاب داور خارجی

                print("\n👨‍🏫 انتخاب داور خارجی:")

                print("-" * 30)

                external_judges = get_available_external_judges()

                if not external_judges:
                    print("❌ هیچ داور خارجی با ظرفیت خالی موجود نیست!")

                    input("\nبرای ادامه Enter بزنید...")

                    continue

                print("\nلیست داوران خارجی available:")

                for i, judge in enumerate(external_judges, 1):
                    print(f"{i}. {judge['name']} - ظرفیت: {judge.get('judge_capacity', 0)}")

                try:

                    choice = int(input("\nشماره داور خارجی را انتخاب کنید: ")) - 1

                    if choice < 0 or choice >= len(external_judges):
                        print("❌ انتخاب نامعتبر!")

                        continue

                    external_judge = external_judges[choice]["user_id"]

                    external_judge_name = external_judges[choice]["name"]

                    print(f"✅ داور خارجی انتخاب شد: {external_judge_name}")


                except (ValueError, IndexError):

                    print("❌ انتخاب نامعتبر!")

                    continue

                # آپدیت درخواست دفاع

                selected_request["status"] = "تایید شده"

                selected_request["approved_date"] = date.today().strftime("%Y-%m-%d")

                selected_request["defense_date"] = defense_date

                selected_request["internal_judge_id"] = internal_judge

                selected_request["external_judge_id"] = external_judge

                # آپدیت فایل درخواست‌ها

                for i, req in enumerate(defense_requests):

                    if req["student_id"] == selected_request["student_id"]:
                        defense_requests[i] = selected_request

                        break

                if write_json("data/requests/defense_requests.json", defense_requests):

                    # کاهش ظرفیت داوران

                    if decrease_judge_capacity(internal_judge, is_external=False) and decrease_judge_capacity(
                            external_judge, is_external=True):

                        print("✅ درخواست دفاع تایید شد و جزئیات ثبت گردید.")

                        print("✅ ظرفیت داوران نیز کاهش یافت.")

                        # نمایش اطلاعات

                        print(f"\n📋 اطلاعات دفاع:")

                        print(f"   📅 تاریخ دفاع: {defense_date}")

                        print(f"   👨‍🏫 داور داخلی: {internal_judge_name}")

                        print(f"   👨‍🏫 داور خارجی: {external_judge_name}")

                    else:

                        print("⚠️ درخواست تایید شد اما کاهش ظرفیت داوران با مشکل مواجه شد!")

                else:

                    print("❌ خطا در ذخیره تغییرات!")

                input("\nبرای ادامه Enter بزنید...")

                break

            elif action == "6":
                # بازگشت به منوی قبلی
                print("بازگشت به منوی اصلی...")
                break

            else:
                print("❌ گزینه نامعتبر!")

            input("\nبرای ادامه Enter بزنید...")

    except (ValueError, IndexError):
        print("❌ انتخاب نامعتبر!")

    input("\nبرای بازگشت Enter بزنید...")


def grade_defense_sessions(professor):
    """نمره‌دهی جلسات دفاع شده"""
    print("\n📊 نمره‌دهی جلسات دفاع شده")
    print("=" * 50)

    # خواندن درخواست‌های دفاع
    defense_requests = read_json("data/requests/defense_requests.json")
    today = date.today()

    # فیلتر کردن درخواست‌هایی که:
    # 1. داور داخلی یا خارجی این استاد باشد
    # 2. وضعیت "تایید شده" داشته باشند
    # 3. تاریخ دفاع گذشته باشد
    professor_defense_requests = [
        r for r in defense_requests
        if (r.get("internal_judge_id") == professor.user_id or r.get("external_judge_id") == professor.user_id)
           and r.get("status") == "تایید شده"
           and "defense_date" in r
    ]

    # فقط درخواست‌هایی که تاریخ دفاعشان گذشته است
    graded_defenses = []
    for req in professor_defense_requests:
        try:
            defense_date = datetime.strptime(req["defense_date"], "%Y-%m-%d").date()
            if defense_date <= today:
                graded_defenses.append(req)
        except ValueError:
            continue

    if not graded_defenses:
        print("✅ هیچ جلسه دفاعی برای نمره‌دهی وجود ندارد.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    print("\n📝 لیست جلسات دفاع شده برای نمره‌دهی:")
    print("=" * 60)

    # خواندن اطلاعات دانشجویان
    students = read_json("data/users/students.json")
    students_dict = {s["user_id"]: s for s in students} if students else {}

    for i, req in enumerate(graded_defenses, 1):
        student_info = students_dict.get(req["student_id"], {})
        student_name = student_info.get("name", "نامشخص")

        # تعیین نقش استاد (داور داخلی یا خارجی)
        role = "داور داخلی" if req.get("internal_judge_id") == professor.user_id else "داور خارجی"

        # بررسی آیا قبلاً نمره داده شده یا نه
        if role == "داور داخلی":
            already_graded = "internal_grade" in req
            grade_display = f"نمره قبلی: {req['internal_grade']}" if already_graded else "نیاز به نمره‌دهی"
        else:
            already_graded = "external_grade" in req
            grade_display = f"نمره قبلی: {req['external_grade']}" if already_graded else "نیاز به نمره‌دهی"

        print(f"\n{i}. 👨‍🎓 دانشجو: {student_name}")
        print(f"   🔢 کد دانشجو: {req['student_id']}")
        print(f"   📚 عنوان: {req.get('title', 'نامشخص')}")
        print(f"   📅 تاریخ دفاع: {req.get('defense_date', 'نامشخص')}")
        print(f"   👨‍🏫 نقش شما: {role}")
        print(f"   📊 وضعیت: {grade_display}")
        print("-" * 40)

    try:
        choice = int(input("\n🎯 شماره دفاع برای نمره‌دهی: ")) - 1

        if choice < 0 or choice >= len(graded_defenses):
            print("❌ شماره دفاع نامعتبر است!")
            input("\nبرای بازگشت Enter بزنید...")
            return

        selected_defense = graded_defenses[choice]
        student_info = students_dict.get(selected_defense["student_id"], {})
        student_name = student_info.get("name", "نامشخص")

        # تعیین نقش استاد
        is_internal_judge = selected_defense.get("internal_judge_id") == professor.user_id
        role = "داور داخلی" if is_internal_judge else "داور خارجی"

        print(f"\n📋 نمره‌دهی برای دفاع دانشجو {student_name} ({role}):")
        print("=" * 50)
        print(f"📚 عنوان: {selected_defense.get('title', 'نامشخص')}")
        print(f"📅 تاریخ دفاع: {selected_defense.get('defense_date', 'نامشخص')}")

        # بررسی آیا قبلاً نمره داده شده
        if (is_internal_judge and "internal_grade" in selected_defense) or (
                not is_internal_judge and "external_grade" in selected_defense):
            print("⚠️  شما قبلاً به این دفاع نمره داده‌اید.")
            change_grade = input("آیا می‌خواهید نمره را تغییر دهید؟ (y/n): ").strip().lower()
            if change_grade != 'y':
                print("❌ نمره‌دهی لغو شد.")
                input("\nبرای بازگشت Enter بزنید...")
                return

        # دریافت نمره
        while True:
            try:
                grade = input("\n💯 نمره را وارد کنید (0-20): ").strip()
                grade_value = float(grade)

                if 0 <= grade_value <= 20:
                    break
                else:
                    print("❌ نمره باید بین 0 تا 20 باشد!")
            except ValueError:
                print("❌ لطفاً یک عدد وارد کنید!")

        # تعیین نمره حروفی
        if grade_value >= 17:
            letter_grade = "الف"
        elif grade_value >= 14:
            letter_grade = "ب"
        elif grade_value >= 10:
            letter_grade = "ج"
        else:
            letter_grade = "د"

        print(f"📊 نمره حروفی: {letter_grade}")

        # تأیید نمره
        confirm = input("\n❓ آیا از نمره وارد شده اطمینان دارید؟ (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ نمره‌دهی لغو شد.")
            input("\nبرای بازگشت Enter بزنید...")
            return

        # آپدیت نمره در درخواست دفاع
        if is_internal_judge:
            selected_defense["internal_grade"] = grade_value
            # selected_defense["internal_letter_grade"] = letter_grade
            selected_defense["internal_grade_date"] = today.strftime("%Y-%m-%d")
        else:
            selected_defense["external_grade"] = grade_value
            # selected_defense["external_letter_grade"] = letter_grade
            selected_defense["external_grade_date"] = today.strftime("%Y-%m-%d")

        # بررسی آیا هر دو داور نمره داده‌اند
        both_graded = "internal_grade" in selected_defense and "external_grade" in selected_defense

        if both_graded:
            print("✅ هر دو داور نمره داده‌اند.")

            # محاسبه نمره نهایی (میانگین دو نمره)
            internal_grade = selected_defense["internal_grade"]
            external_grade = selected_defense["external_grade"]
            final_grade = (internal_grade + external_grade) / 2

            # تعیین نمره حروفی نهایی
            if final_grade >= 17:
                final_letter_grade = "الف"
            elif final_grade >= 14:
                final_letter_grade = "ب"
            elif final_grade >= 10:
                final_letter_grade = "ج"
            else:
                final_letter_grade = "د"

            selected_defense["final_grade"] = final_grade
            selected_defense["final_letter_grade"] = final_letter_grade
            selected_defense["status"] = "مختومه"

            print(f"🎯 نمره نهایی: {final_grade:.2f} ({final_letter_grade})")
            print("✅ پایان‌نامه مختومه شد.")

            # کپی به فایل defended_theses.json (نه انتقال)
            defended_theses = read_json("data/theses/defended_theses.json")
            defended_theses.append(selected_defense.copy())  # کپی کردن object
            write_json("data/theses/defended_theses.json", defended_theses)

            print("✅ اطلاعات پایان‌نامه به آرشیو اضافه شد.")
        else:
            print("✅ نمره شما ثبت شد.")
            # وضعیت تغییر نمی‌کند (همچنان "تایید شده" باقی می‌ماند)

        # ذخیره تغییرات در defense_requests.json
        for i, req in enumerate(defense_requests):
            if req["student_id"] == selected_defense["student_id"]:
                defense_requests[i] = selected_defense
                break

        write_json("data/requests/defense_requests.json", defense_requests)
        print("✅ نمره با موفقیت ثبت شد.")

    except (ValueError, IndexError):
        print("❌ انتخاب نامعتبر!")

    # افزایش ظرفیت داور خارجی پس از نمره‌دهی
    professors = read_json("data/users/professors.json")
    for judge in professors:
        if judge["user_id"] == professor.user_id:
            judge["judge_capacity"] = judge.get("judge_capacity", 0) + 1
            print(f"✅ ظرفیت داوری شما به {judge['judge_capacity']} افزایش یافت.")
            break

    write_json("data/users/professors.json", professors)

    input("\nبرای بازگشت Enter بزنید...")

def search_theses():
    """جستجو در بانک پایان‌نامه‌ها"""
    print("\n🔍 جستجو در بانک پایان‌نامه‌های مختومه")
    print("=" * 50)

    print("\n📋 انواع جستجو:")
    print("1. عنوان پایان‌نامه")
    print("2. نام استاد راهنما")
    print("3. کلمات کلیدی")
    print("4. نام نویسنده (دانشجو)")
    print("5. سال دفاع")
    print("6. نام داوران")

    try:
        choice = input("\n🎯 نوع جستجو را انتخاب کنید (1-6): ").strip()
        search_types = {
            "1": "title",
            "2": "professor",
            "3": "keywords",
            "4": "author",
            "5": "year",
            "6": "judges"
        }

        if choice not in search_types:
            print("❌ انتخاب نامعتبر!")
            input("\nبرای بازگشت Enter بزنید...")
            return

        search_query = input("🔍 عبارت جستجو را وارد کنید: ").strip()

        if not search_query:
            print("❌ عبارت جستجو نمی‌تواند خالی باشد!")
            input("\nبرای بازگشت Enter بزنید...")
            return

        # انجام جستجو
        from src.utils.helpers import search_theses, open_file
        results = search_theses(search_query, search_types[choice])

        # نمایش نتایج
        print(f"\n✅ تعداد نتایج یافت شده: {len(results)}")
        print("=" * 60)

        if not results:
            print("❌ هیچ نتیجه‌ای یافت نشد.")
        else:
            # خواندن اطلاعات کاربران
            students = read_json("data/users/students.json")
            professors = read_json("data/users/professors.json")
            external_judges = read_json("data/users/external_judges.json")

            students_dict = {s["user_id"]: s for s in students}
            professors_dict = {p["user_id"]: p for p in professors}
            external_judges_dict = {j["user_id"]: j for j in external_judges}

            for i, thesis in enumerate(results, 1):
                # پیدا کردن نام‌ها
                student_name = students_dict.get(thesis.get("student_id", ""), {}).get("name", "نامشخص")
                professor_name = professors_dict.get(thesis.get("professor_id", ""), {}).get("name", "نامشخص")
                internal_judge_name = professors_dict.get(thesis.get("internal_judge_id", ""), {}).get("name", "نامشخص")
                external_judge_name = external_judges_dict.get(thesis.get("external_judge_id", ""), {}).get("name", "نامشخص")

                from src.utils.helpers import get_semester_year

                if thesis.get("defense_date"):
                    semester_info = get_semester_year(thesis["defense_date"])

                print(f"\n{i}. 📚 عنوان: {thesis.get('title', 'نامشخص')}")
                print(f"   📝 چکیده: {thesis.get('abstract', 'نامشخص')[:100]}...")  # نمایش 100 کاراکتر اول
                print(f"   🔖 کلمات کلیدی: {', '.join(thesis.get('keywords', []))}")
                print(f"   👨‍🎓 نویسنده: {student_name}")
                print(f"   📅 سال/نیمسال: {semester_info}")
                print(f"   👨‍🏫 استاد راهنما: {professor_name}")
                print(f"   👨‍⚖️ داور داخلی: {internal_judge_name}")
                print(f"   👨‍⚖️ داور خارجی: {external_judge_name}")
                print(f"   📊 نمره: {thesis.get('final_grade', 'نامشخص')}")
                print(f"   🏆 نمره حروفی: {thesis.get('final_letter_grade', 'نامشخص')}")
                print(f"   📁 فایل: {thesis.get('file_path', 'نامشخص')}")
                print("-" * 60)

        # نمایش منوی مدیریت نتایج
        if results:
            print("\n📋 مدیریت نتایج:")
            print("1. باز کردن فایل یک پایان‌نامه")
            print("2. بازگشت به منوی اصلی")

            manage_choice = input("لطفاً گزینه مورد نظر را انتخاب کنید: ").strip()

            if manage_choice == "1":
                try:
                    thesis_choice = int(input("شماره پایان‌نامه برای باز کردن فایل: ")) - 1
                    if 0 <= thesis_choice < len(results):
                        thesis = results[thesis_choice]
                        if thesis.get('file_path'):
                            file_path = get_full_path(thesis['file_path'])
                            if os.path.exists(file_path):
                                open_file(file_path)
                                print("✅ فایل باز شد.")
                            else:
                                print("❌ فایل پیدا نشد!")
                        else:
                            print("❌ فایلی برای این پایان‌نامه وجود ندارد.")
                    else:
                        print("❌ شماره نامعتبر!")
                except ValueError:
                    print("❌ لطفاً عدد وارد کنید!")

    except Exception as e:
        print(f"❌ خطا در جستجو: {e}")

    input("\nبرای بازگشت Enter بزنید...")


def change_password(professor):
    """تغییر رمز عبور"""
    print("\n🔒 تغییر رمز عبور")
    print("-" * 40)

    old_password = input("رمز عبور فعلی: ")
    new_password = input("رمز عبور جدید: ")
    confirm_password = input("تکرار رمز عبور جدید: ")

    # استفاده از تابع change_password از auth.py
    from src.utils.auth import change_password as auth_change_password
    auth_change_password(professor, old_password, new_password, confirm_password)

    input("\nبرای بازگشت Enter بزنید...")