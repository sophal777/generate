import os
import random
import sys
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QVBoxLayout,QSpinBox

output_dir = "phones_output"
os.makedirs(output_dir, exist_ok=True)

def generate_and_validate_phone(country):
    if country == "KH":
        phone = random.choice(['+85596', '+85597', '+85588', '+85571']) + str(random.randint(1000000, 9999999))
    elif country == "TH":
        phone = random.choice(['+6691', '+6683', '+6686', '+6687']) + str(random.randint(1000000, 9999999))
    elif country == "US":
        phone = '+1' + str(random.randint(2000000000, 9999999999))
    elif country == "VN":
        phone = random.choice(['+8491', '+8490', '+8488', '+8493']) + str(random.randint(1000000, 9999999))
    elif country == "JP":
        phone = '+81' + str(random.randint(70, 90)) + str(random.randint(10000000, 99999999))
    else:
        return None

    try:
        parsed = phonenumbers.parse(phone, None)
        if phonenumbers.is_valid_number(parsed):
            return phone
    except NumberParseException:
        pass
    return None
def ph():
# បញ្ជីប្រទេស
    countries = ["KH", "TH", "US", "VN", "JP"]

    for _ in range(50):
        c = random.choice(countries)
        phone = generate_and_validate_phone(c)
        if phone:
            with open("phones_output/valid_phone.txt", mode="a", encoding="utf-8") as f:
                f.write(phone + "\n")
            print(f"✅ Valid ({c}): {phone}")
        else:
            print(f"❌ Invalid ({c})")



def generate_and_validate_phone(country):
    if country == "KH":
        phone = random.choice(['+85596', '+85597', '+85588', '+85571']) + str(random.randint(1000000, 9999999))
    elif country == "TH":
        phone = random.choice(['+6691', '+6683', '+6686', '+6687']) + str(random.randint(1000000, 9999999))
    elif country == "US":
        phone = '+1' + str(random.randint(2000000000, 9999999999))
    elif country == "VN":
        phone = random.choice(['+8491', '+8490', '+8488', '+8493']) + str(random.randint(1000000, 9999999))
    elif country == "JP":
        phone = '+81' + str(random.randint(70, 90)) + str(random.randint(10000000, 99999999))
    else:
        return None

    try:
        parsed = phonenumbers.parse(phone, None)
        if phonenumbers.is_valid_number(parsed):
            return phone
    except NumberParseException:
        pass
    return None
def phY():
    countries = ["KH", "TH", "US", "VN", "JP"]

    for _ in range(100):
        c = random.choice(countries)
        phone = generate_and_validate_phone(c)
        if phone:
            file_path = os.path.join(output_dir, f"{c}_phones.txt")
            with open(file_path, mode="a", encoding="utf-8") as f:
                f.write(phone + "\n")
            print(f"✅ Valid ({c}): {phone}")
        else:
            print(f"❌ Invalid ({c})")


def random_khmer_name():
    khmer_first_names = ['សុភា', 'ចាន់ដា', 'រ័ត្ន', 'ស្រីពៅ']
    khmer_last_names = ['ឈឿន', 'សោម', 'សុខ', 'ជាតិ']
    return random.choice(khmer_first_names), random.choice(khmer_last_names)

def random_english_name():
    english_first_names = ['John', 'Jane', 'Alex', 'Emily']
    english_last_names = ['Smith', 'Johnson', 'Brown', 'Lee']
    return random.choice(english_first_names), random.choice(english_last_names)

def random_korean_name():
    korean_first_names = ['지수', '민호', '현', '수진']  # Korean Hangul
    korean_last_names = ['김', '박', '이', '최']
    return random.choice(korean_first_names), random.choice(korean_last_names)

def random_thai_name():
    thai_first_names = ['สมชาย', 'สุดา', 'นิรันดร์', 'อนงค์']  # Thai script
    thai_last_names = ['ชัย', 'พันธ์', 'ลิ้ม', 'จันทร์']
    return random.choice(thai_first_names), random.choice(thai_last_names)

# Get names
thai_first_name, thai_last_name = random_thai_name()
khmer_first_name, khmer_last_name = random_khmer_name()
english_first_name, english_last_name = random_english_name()
korean_first_name, korean_last_name = random_korean_name()

# Print
print("Thai:", thai_first_name, thai_last_name)
print("Khmer:", khmer_first_name, khmer_last_name)
print("English:", english_first_name, english_last_name)
print("Korean:", korean_first_name, korean_last_name)

#phY()
#ph()
