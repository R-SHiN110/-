from src.utils.helpers import display_menu
from src.utils.file_io import read_json, write_json
from src.utils.auth import find_user_by_id
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import shutil
import os
from src.utils.file_io import get_full_path


def show_student_menu(student):
    """نمایش منوی اصلی دانشجو"""
    while True:
        menu_title = f"منوی دانشجو - {student.name}"
        options = [
            "درخواست اخذ درس پایان‌نامه",
            "ارسال درخواست دفاع پایان‌نامه",
            "مشاهده وضعیت درخواست‌ ها",
            "جستجو در بانک پایان‌نامه‌ها",
            "تغییر رمز عبور",
            "خروج از حساب کاربری"
        ]

        display_menu(menu_title, options)

        choice = input("لطفاً گزینه مورد نظر را انتخاب کنید: ").strip()

        if choice == "1":
            request_thesis_course(student)
        elif choice == "2":
            request_defense(student)
        elif choice == "3":
            view_request_status(student)
        elif choice == "4":
            search_theses()
        elif choice == "5":
            change_password(student)
        elif choice == "6":
            print("خروج از حساب کاربری...")
            break
        else:
            print("⚠️  گزینه نامعتبر!")
            input("برای ادامه Enter بزنید...")


def request_thesis_course(student):
    """درخواست اخذ درس پایان‌نامه"""
    print("\n📝 درخواست اخذ درس پایان‌نامه")
    print("=" * 50)

    # خواندن لیست دروس از فایل
    courses = read_json("data/courses/thesis_courses.json")

    if not courses:
        print("❌ هیچ درسی در سیستم وجود ندارد.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    # فقط دروسی که عنوان آنها با "پایان‌نامه" شروع می‌شود
    thesis_courses = [c for c in courses if c["title"].startswith("پایان نامه")]

    if not thesis_courses:
        print("❌ هیچ درس پایان‌نامه‌ای در سیستم وجود ندارد.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    # نمایش دروس موجود
    available_courses = [c for c in courses if c["capacity"] > 0]

    if not available_courses:
        print("❌ هیچ درسی با ظرفیت خالی وجود ندارد.")
        input("\nبرای بازگشت Enter بزنید...")
        return



    # بررسی اینکه آیا دانشجو قبلاً برای این درس درخواست داده یا نه
    requests = read_json("data/requests/enrollment_requests.json")

    # بررسی جدید: آیا دانشجو قبلاً برای ANY درس پایان‌نامه درخواست داده؟
    existing_thesis_request = next((r for r in requests
                                    if r["student_id"] == student.user_id
                                    and any(c["course_id"] == r["course_id"] for c in thesis_courses)), None)

    if existing_thesis_request:
        # پیدا کردن اطلاعات درس مربوطه
        print("❌ شما قبلاً برای درس 'پایان نامه' درخواست داده‌اید!")
        print("⚠️  امکان برداشتن بیش از یک درس پایان‌نامه وجود ندارد.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    print("\n🎓 لیست دروس پایان‌نامه :")

    for course in available_courses:
        # پیدا کردن نام استاد
        professor_data = find_user_by_id(course["professor_id"], "professor")
        professor_name = professor_data["name"] if professor_data else "نامشخص"
        print(f"\n🔹 کد درس: {course['course_id']}")
        print(f"   📚 عنوان: {course['title']}")
        print(f"   👨‍🏫 استاد: {professor_name}")
        print(f"   📅 سال/نیمسال: {course['year']} / {course['semester']}")
        print(f"   👥 ظرفیت: {course['capacity']} نفر")
        print(f"   🕒 جلسات: {course['sessions_count']} جلسه")
        print(f"   📘 واحدها: {course['units']} واحد")
        print(f"   📂 منابع: {course['resources']}")
        print("-" * 40)

    # دریافت کد درس از کاربر
    course_id = input("\n🎯 لطفاً کد درس مورد نظر را وارد کنید: ").strip()

    # پیدا کردن درس انتخاب شده
    selected_course = next((c for c in available_courses if c["course_id"] == course_id), None)

    if not selected_course:
        print("❌ کد درس نامعتبر یا اشتباه است!")
        input("\nبرای بازگشت Enter بزنید...")
        return

    # تایید نهایی از کاربر
    professor_data = find_user_by_id(selected_course["professor_id"], "professor")
    professor_name = professor_data["name"] if professor_data else "نامشخص"

    print(f"\n📋 اطلاعات درس انتخابی:")
    print(f"   🔹 کد درس: {selected_course['course_id']}")
    print(f"   📚 عنوان: {selected_course['title']}")
    print(f"   👨‍🏫 استاد: {professor_name}")
    print(f"   📅 سال/نیمسال: {selected_course['year']} / {selected_course['semester']}")

    confirm = input("\n❓ آیا از انتخاب خود مطمئن هستید؟ (y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ درخواست لغو شد.")
        input("\nبرای بازگشت Enter بزنید...")
        return


    from datetime import date
    new_request = {
        "student_id": student.user_id,
        "course_id": selected_course["course_id"],
        "professor_id": selected_course["professor_id"],
        "status": "در انتظار تأیید استاد",
        "created_at": date.today().strftime("%Y-%m-%d"),
        "approved_date": "-",  # مقدار پیش‌فرض تا زمانی که استاد تایید نکند
        "rejected_date": "-"  # مقدار پیش‌فرض برای رد شدن
    }

    requests.append(new_request)

    # پیدا کردن درس در لیست اصلی courses و کم کردن ظرفیت
    for course in courses:
        if course["course_id"] == selected_course["course_id"]:
            if course["capacity"] > 0:
                course["capacity"] -= 1
                print(f"✅ ظرفیت درس به {course['capacity']} کاهش یافت.")
            else:
                print("❌ خطا: ظرفیت درس قبلاً پر شده است!")
                input("\nبرای بازگشت Enter بزنید...")
                return
            break

    if write_json("data/requests/enrollment_requests.json", requests):
        if write_json("data/courses/thesis_courses.json", courses):
            print("\n✅ درخواست شما با موفقیت ثبت شد و برای استاد ارسال گردید.")

        # نمایش اطلاعات درخواست
        print(f"\n📋 اطلاعات درخواست:")
        print(f"   📚 درس: {selected_course['title']}")
        print(f"   👨‍🏫 استاد: {professor_name}")
        print(f"   📅 تاریخ درخواست: {new_request['created_at']}")
        print(f"   📊 وضعیت: {new_request['status']}")
    else:
        print("❌ خطا در ثبت درخواست!")

    input("\nبرای بازگشت Enter بزنید...")


def request_defense(student):
    """ارسال درخواست دفاع"""
    print("\n🎓 ارسال درخواست دفاع")
    print("=" * 50)

    # خواندن درخواست‌های اخذ پایان‌نامه
    enrollment_requests = read_json("data/requests/enrollment_requests.json")

    # پیدا کردن درخواست تایید شده دانشجو
    approved_request = next((r for r in enrollment_requests
                             if r["student_id"] == student.user_id
                             and r["status"] == "تایید شده"), None)

    if not approved_request:
        print("❌ شما بدلیل وضعیت درس امکان درخواست دفاع ندارید.")
        print("ℹ️  یا درخواستی ثبت نکرده‌اید یا درخواست شما هنوز تایید نشده است.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    # بررسی جدید: آیا دانشجو قبلاً درخواست دفاعی دارد که رد نشده باشد؟
    defense_requests = read_json("data/requests/defense_requests.json")
    existing_defense_request = next((r for r in defense_requests
                                     if r["student_id"] == student.user_id
                                     and r["status"] != "رد شده"), None)

    if existing_defense_request:
        print("❌ شما قبلاً درخواست دفاع داده‌اید!")
        print(f"📊 وضعیت درخواست قبلی: {existing_defense_request['status']}")

        if existing_defense_request["status"] == "در انتظار تأیید استاد":
            print("ℹ️  لطفاً منتظر بررسی استاد راهنما بمانید.")
        elif existing_defense_request["status"] == "تایید شده":
            print("ℹ️  درخواست دفاع شما قبلاً تایید شده است.")

        input("\nبرای بازگشت Enter بزنید...")
        return

    # بررسی تاریخ تایید - فقط اگر approved_date متفاوت از "-" باشد
    if approved_request.get("approved_date") == "-":
        print("❌ خطا در اطلاعات درخواست! تاریخ تایید ثبت نشده است.")
        print("ℹ️  لطفاً با استاد راهنما یا پشتیبانی تماس بگیرید.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    try:
        approval_date = datetime.strptime(approved_request["approved_date"], "%Y-%m-%d").date()
        today = date.today()
        deadline = approval_date + relativedelta(months=3)

        if today < deadline:
            print("⏳ اخطار: هنوز سه ماه از تاریخ تایید نگذشته است ⏳")

            # محاسبه زمان گذشته و مانده
            time_passed = relativedelta(today, approval_date)
            time_remaining = relativedelta(deadline, today)

            print(f"📅 تاریخ تایید استاد: {approval_date}")
            print(f"⏰ از تاریخ تایید: {time_passed.months} ماه و {time_passed.days} روز گذشته است")
            print(
                f"⏳ شما {time_remaining.months} ماه و {time_remaining.days} روز دیگر می‌توانید برای ارسال درخواست دفاع اقدام کنید")

            input("\nبرای بازگشت Enter بزنید...")
            return

        # اگر سه ماه گذشته باشد
        print("✅ سه ماه از تاریخ تایید درخواست شما گذشته است")
        print(f"📅 تاریخ تایید استاد: {approval_date}")
        print("⬅️ درصورت آمادگی برای برگزاری جلسه دفاع، عدد 1 را وارد کنید:")

        choice = input("👉 ").strip()

        if choice == '1':
            print("\n📋 لطفا اطلاعات خواسته شده را تکمیل کنید:")
            print("-" * 40)

            # دریافت اطلاعات پایان‌نامه
            title = input("عنوان پایان‌نامه: ").strip()
            abstract = input("چکیده پایان‌نامه: ").strip()
            keywords_input = input("کلمات کلیدی (با '-' جدا کنید): ").strip()
            keywords = [k.strip() for k in keywords_input.split('-')] if keywords_input else []

            # دریافت مسیر فایل PDF
            print("\n📁 آپلود فایل پایان‌نامه:")
            print("ℹ️  لطفاً مسیر کامل فایل PDF پایان‌نامه خود را وارد کنید")
            pdf_path = input("مسیر فایل PDF: ").strip()

            # دریافت مسیر عکس صفحه اول
            print("\n📸 آپلود عکس صفحه اول پایان‌نامه:")
            print("ℹ️  لطفاً از صفحه اول پی‌دی‌اف عکس بگیرید و مسیر فایل عکس را وارد کنید")
            first_page_path = input("مسیر عکس صفحه اول: ").strip()

            # دریافت مسیر عکس صفحه آخر
            print("\n📸 آپلود عکس صفحه آخر پایان‌نامه:")
            print("ℹ️  لطفاً از صفحه آخر پی‌دی‌اف عکس بگیرید و مسیر فایل عکس را وارد کنید")
            last_page_path = input("مسیر عکس صفحه آخر: ").strip()

            # بررسی وجود عکس‌ها
            image_paths = [first_page_path, last_page_path]
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    print(f"❌ فایل عکس پیدا نشد: {img_path}")
                    input("\nبرای بازگشت Enter بزنید...")
                    return
                if not img_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"❌ فرمت فایل عکس نامعتبر است: {img_path}")
                    print("ℹ️  فقط فایل‌های JPG, JPEG, PNG قابل قبول هستند!")
                    input("\nبرای بازگشت Enter بزنید...")
                    return

            # بررسی وجود فایل
            if not os.path.exists(pdf_path):
                print("❌ فایل PDF پیدا نشد! لطفاً مسیر را بررسی کنید.")
                input("\nبرای بازگشت Enter بزنید...")
                return

            if not pdf_path.lower().endswith('.pdf'):
                print("❌ فقط فایل‌های PDF قابل قبول هستند!")
                input("\nبرای بازگشت Enter بزنید...")
                return

            # ایجاد نام فایل‌های جدید
            base_filename = f"{student.user_id}.{approved_request['course_id']}"
            pdf_filename = f"{base_filename}.pdf"
            first_page_filename = f"{base_filename}.page1.jpg"
            last_page_filename = f"{base_filename}.page2.jpg"

            # استفاده از get_full_path برای مسیر درست

            documents_dir = get_full_path("documents")
            theses_dir = os.path.join(documents_dir, "theses")
            images_dir = os.path.join(documents_dir, "images")

            # ایجاد پوشه‌های مقصد اگر وجود ندارند
            os.makedirs(theses_dir, exist_ok=True)
            os.makedirs(images_dir, exist_ok=True)

            # مسیرهای مقصد
            pdf_destination = os.path.join(theses_dir, pdf_filename)
            first_page_destination = os.path.join(images_dir, first_page_filename)
            last_page_destination = os.path.join(images_dir, last_page_filename)

            # کپی فایل به مقصد
            try:
                # کپی فایل‌ها به مقصد
                shutil.copy2(pdf_path, pdf_destination)
                shutil.copy2(first_page_path, first_page_destination)
                shutil.copy2(last_page_path, last_page_destination)

                print("✅ تمام فایل‌ها با موفقیت آپلود شدند:")
                print(f"   📄 فایل PDF: {pdf_filename}")
                print(f"   📸 عکس صفحه اول: {first_page_filename}")
                print(f"   📸 عکس صفحه آخر: {last_page_filename}")

                # ذخیره مسیرهای نسبی برای JSON
                relative_pdf_path = f"documents/theses/{pdf_filename}"
                relative_image_path = [f"documents/images/{base_filename}.page1.jpg",
                                       f"documents/images/{base_filename}.page2.jpg"]

            except Exception as e:
                print(f"❌ خطا در آپلود فایل: {e}")
                input("\nبرای بازگشت Enter بزنید...")
                return

            # ایجاد درخواست دفاع
            defense_requests = read_json("data/requests/defense_requests.json")
            # new_request_id = get_next_id(defense_requests, "defense_request")

            new_defense_request = {
                "student_id": student.user_id,
                "professor_id": approved_request["professor_id"],
                "title": title,
                "abstract": abstract,
                "keywords": keywords,
                "status": "در انتظار تأیید استاد",
                "submission_date": today.strftime("%Y-%m-%d"),
                "file_path": relative_pdf_path,  # مسیر فایل PDF
                "image_path": relative_image_path  # مسیر تصاویر
            }

            defense_requests.append(new_defense_request)

            if write_json("data/requests/defense_requests.json", defense_requests):
                print("\n✅ درخواست دفاع شما با موفقیت ثبت شد و برای استاد ارسال گردید.")
                # print(f"📋 کد درخواست دفاع: {new_request_id}")
            else:
                print("❌ خطا در ثبت درخواست دفاع!")

        else:
            print("❌ گزینه نامعتبر! درخواست لغو شد.")

    except ValueError:
        print("❌ خطا در فرمت تاریخ! لطفاً با پشتیبانی تماس بگیرید.")
    except Exception as e:
        print(f"❌ خطای ناشناخته: {e}")

    input("\nبرای بازگشت Enter بزنید...")


def view_request_status(student):
    """مشاهده وضعیت آخرین درخواست دانشجو"""
    # print("\n📊 وضعیت آخرین درخواست های شما")
    # print("=" * 50)

    # خواندن درخواست‌های اخذ پایان‌نامه
    requests = read_json("data/requests/enrollment_requests.json")

    # جستجو از انتهای لیست برای پیدا کردن آخرین درخواست اخذ
    latest_request = None
    for i in range(len(requests) - 1, -1, -1):
        if requests[i]["student_id"] == student.user_id:
            latest_request = requests[i]
            break

    if not latest_request:
        print("❌ درخواستی ثبت نشده است.")
        print("ℹ️  از بخش 'درخواست اخذ درس پایان‌نامه' می‌توانید برای درخواست اقدام کنید.")
        input("\nبرای بازگشت Enter بزنید...")
        return

    # خواندن اطلاعات دروس
    courses = read_json("data/courses/thesis_courses.json")
    courses_dict = {c["course_id"]: c for c in courses} if courses else {}

    # خواندن اطلاعات اساتید
    professors = read_json("data/users/professors.json")
    professors_dict = {p["user_id"]: p for p in professors} if professors else {}

    # نمایش اطلاعات آخرین درخواست
    course_info = courses_dict.get(latest_request["course_id"], {})
    professor_info = professors_dict.get(latest_request["professor_id"], {})

    course_title = course_info.get("title", "نامشخص")
    professor_name = professor_info.get("name", "نامشخص")

    print()
    print("🔹 اطلاعات درخواست اخذ درس پایان نامه: ")
    print(f"👨‍🏫 استاد: {professor_name}")
    print(f"📅 تاریخ درخواست: {latest_request.get('created_at', 'نامشخص')}")
    print(f"📊 وضعیت: {latest_request['status']}")
    print("-" * 50)

    # نمایش پیام راهنمایی بر اساس وضعیت آخرین درخواست
    # print("\n💡 راهنمایی:")
    # print("-" * 40)

    if latest_request["status"] == "رد شده":
        print("\n💡 راهنمایی:")
        print("-" * 40)
        print("❌ این درخواست رد شده است.")
        print("ℹ️  برای درخواست مجدد به بخش 'درخواست اخذ پایان‌نامه' مراجعه کنید.")

    elif latest_request["status"] == "در انتظار تأیید استاد":
        print("\n💡 راهنمایی:")
        print("-" * 40)
        print("⏳ این درخواست در حال بررسی است.")
        print("ℹ️  لطفاً منتظر تایید استاد بمانید.")

    elif latest_request["status"] == "تایید شده":
        # print("✅ این درخواست تایید شده است.")

        # بررسی وضعیت درخواست دفاع - جستجو از انتهای لیست
        defense_requests = read_json("data/requests/defense_requests.json")
        latest_defense_request = None

        # جستجو از انتهای لیست برای پیدا کردن آخرین درخواست دفاع
        for i in range(len(defense_requests) - 1, -1, -1):
            if defense_requests[i]["student_id"] == student.user_id:
                latest_defense_request = defense_requests[i]
                break

        if latest_defense_request:
            print(f"🎓 وضعیت درخواست دفاع: {latest_defense_request['status']}")

            if latest_defense_request["status"] == "در انتظار تأیید استاد":
                print("⏳ درخواست دفاع شما در حال بررسی توسط استاد راهنما است.")
                print(f"📅 تاریخ ارسال درخواست دفاع: {latest_defense_request.get('submission_date', 'نامشخص')}")
            elif latest_defense_request["status"] == "تایید شده":
                print("✅ درخواست دفاع شما تایید شده است.")
                print("ℹ️  آماده‌سازی برای جلسه دفاع را آغاز کنید.")
                print(f"📅 تاریخ تایید دفاع: {latest_defense_request.get('approved_date', 'نامشخص')}")
            elif latest_defense_request["status"] == "رد شده":
                print("❌ درخواست دفاع شما رد شده است.")
                print("ℹ️  می‌توانید مجدداً درخواست دفاع ثبت کنید.")
                print(f"📅 تاریخ رد درخواست دفاع: {latest_defense_request.get('rejected_date', 'نامشخص')}")

        else:
            # بررسی امکان درخواست دفاع
            if latest_request.get("approved_date") != "-":
                try:
                    approval_date = datetime.strptime(latest_request["approved_date"], "%Y-%m-%d").date()
                    today = date.today()
                    three_months_later = approval_date + relativedelta(months=3)

                    print(f"📅 تاریخ تایید استاد: {approval_date}")

                    if today >= three_months_later:
                        print("🎯 سه ماه از تایید درخواست شما گذشته است. می‌توانید برای درخواست دفاع اقدام کنید!")
                    else:
                        remaining = relativedelta(three_months_later, today)
                        print(f"⏳ تا امکان درخواست دفاع: {remaining.months} ماه و {remaining.days} روز باقی مانده است.")

                except ValueError:
                    print("ℹ️  اگر سه ماه از تایید درخواست شما گذشته باشد، می‌توانید برای درخواست دفاع اقدام کنید.")
            else:
                print("ℹ️  منتظر ثبت تاریخ تایید توسط استاد هستیم...")

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

def change_password(student):
    """تغییر رمز عبور"""
    print("\n🔒 تغییر رمز عبور")
    print("-" * 40)

    old_password = input("رمز عبور فعلی: ")
    new_password = input("رمز عبور جدید: ")
    confirm_password = input("تکرار رمز عبور جدید: ")

    # استفاده از تابع change_password از auth.py
    from src.utils.auth import change_password as auth_change_password
    auth_change_password(student, old_password, new_password, confirm_password)

    input("\nبرای بازگشت Enter بزنید...")


