from src.menus.main_menu import show_main_menu


def main():
    """تابع اصلی برای اجرای برنامه"""
    print ("=" * 60)
    print("       سامانه مدیریت پایان‌نامه‌ها - خوش آمدید")
    print("=" * 60)

    while True:
        show_main_menu()


if __name__ == "__main__":
    main()
    input()