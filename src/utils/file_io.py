import json
import os
from typing import Any, Dict, List

# پیدا کردن مسیر root پروژه
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_full_path(relative_path: str) -> str:
    """تبدیل مسیر نسبی به مسیر مطلق نسبت به root پروژه"""
    return os.path.join(PROJECT_ROOT, relative_path)


def read_json(file_path: str) -> List[Dict[str, Any]]:
    """
    خواندن داده از یک فایل JSON و بازگرداندن آن به صورت لیستی از دیکشنری‌ها.
    اگر فایل وجود نداشت، یک لیست خالی برمی‌گرداند.
    """
    try:
        full_path = get_full_path(file_path)

        # اگر فایل وجود ندارد، ایجادش کن
        if not os.path.exists(full_path):
            # اطمینان از وجود پوشه مقصد
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            # ایجاد فایل با محتوای خالی
            with open(full_path, 'w', encoding='utf-8') as file:
                json.dump([], file, ensure_ascii=False, indent=4)
            return []

        # خواندن فایل با encodingهای مختلف
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1256']

        for encoding in encodings:
            try:
                with open(full_path, 'r', encoding=encoding) as file:
                    data = json.load(file)
                    # print(f"✅ فایل {file_path} با encoding {encoding} خوانده شد")
                    return data
            except UnicodeDecodeError:
                continue
            except json.JSONDecodeError:
                # اگر فایل JSON معتبر نیست، آن را بازنویسی کنیم
                # print(f"⚠️  فایل {file_path} معتبر نیست، در حال بازنویسی...")
                with open(full_path, 'w', encoding='utf-8') as file:
                    json.dump([], file, ensure_ascii=False, indent=4)
                return []

        # اگر هیچ encodingی کار نکرد
        print(f"❌ نتوانستیم فایل {file_path} را با encodingهای مختلف بخوانیم")
        return []

    except Exception as e:
        print(f"❌ خطای ناشناخته در خواندن فایل {file_path}: {e}")
        return []


def write_json(file_path: str, data: List[Dict[str, Any]]) -> bool:
    """
    نوشتن داده (لیستی از دیکشنری‌ها) به یک فایل JSON.
    بازگشت: True در صورت موفقیت، False در صورت خطا
    """
    try:
        full_path = get_full_path(file_path)
        # اطمینان از وجود پوشه مقصد
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"❌ خطا در نوشتن فایل {file_path}: {e}")
        return False

def get_next_id(existing_data: List[Dict[str, Any]], id_field: str = "id") -> str:
    """
    تولید یک ID منحصر به فرد برای رکورد جدید.
    فرض بر این است که IDها از الگوی 'number_' پیروی می‌کنند (مانند 'request_1').
    """
    if not existing_data:
        return f"{id_field}_1"

    # استخراج عدد از آخرین ID
    last_id = existing_data[-1].get(id_field, f"{id_field}_0")
    try:
        last_number = int(last_id.split('_')[-1])
        new_number = last_number + 1
    except (IndexError, ValueError):
        new_number = len(existing_data) + 1

    return f"{id_field}_{new_number}"


def save_uploaded_file(upload_folder: str, file_name: str, file_content: bytes) -> str:
    """
    ذخیره یک فایل آپلود شده (مانند PDF یا JPG) در پوشه مشخص.
    بازگشت: مسیر نسبی فایل ذخیره شده
    """
    try:
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file_name)

        with open(file_path, 'wb') as file:
            file.write(file_content)

        return file_path
    except Exception as e:
        print(f"خطا در ذخیره فایل {file_name}: {e}")
        return ""
