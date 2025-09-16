from src.utils.helpers import display_menu
from src.menus.student_menu import show_student_menu
from src.menus.professor_menu import show_professor_menu
from src.menus.external_judge_menu import external_judge_menu


def show_main_menu():
    """نمایش منوی اصلی و انتخاب نقش"""
    menu_title = "منوی اصلی"
    options = [
        "ورود به عنوان دانشجو",
        "ورود به عنوان استاد",
        "ورود به عنوان داور خارجی",
        "خروج از سیستم"
    ]

    display_menu(menu_title, options)

    choice = input("لطفاً گزینه مورد نظر را انتخاب کنید: ").strip()

    if choice == "1":
        show_login_menu("student")
    elif choice == "2":
        show_login_menu("professor")
    elif choice == "3":
        show_login_menu("external_judge")
    elif choice == "4":
        print("با تشکر از استفاده شما. خداحافظ!")
        exit()
    else:
        print("⚠️  گزینه نامعتبر! لطفاً عدد بین 1 تا 3 وارد کنید.")
        input("برای ادامه Enter بزنید...")


def show_login_menu(role: str):
    """نمایش منوی ورود برای نقش مشخص"""
    role_persian = "دانشجو" if role == "student" else "استاد"

    print(f"\nورود به سیستم به عنوان {role_persian}")
    print("-" * 40)

    user_id = input("کد کاربری: ").strip()
    password = input("رمز عبور: ").strip()

    # بررسی اعتبار کاربر
    from src.utils.auth import verify_user
    user = verify_user(user_id, password, role)
    # کاربر را تبدیل به شی از کلاس دانشجو یا استاد میکند و داخل user میگذارد.

    if user:
        print(f"\n✅ ورود موفق! خوش آمدید {user.name}")
        input("برای ادامه Enter بزنید...")

        # هدایت به منوی مناسب
        if role == "student":
            show_student_menu(user)
        elif role == "professor":
            show_professor_menu(user)
        else:
            external_judge_menu(user)
    else:
        print("\n❌ کد کاربری یا رمز عبور اشتباه است!")
        input("برای بازگشت Enter بزنید...")