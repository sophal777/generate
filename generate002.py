import os
import random
import sys
import threading
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QComboBox,
    QVBoxLayout, QSpinBox, QTextEdit, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# Output directory
output_dir = "phones_output"
os.makedirs(output_dir, exist_ok=True)

# Lock for thread-safe file writing
file_lock = threading.Lock()

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
        return None

def random_khmer_name():
    khmer_first_names = ['សុភា', 'ចាន់ដា', 'រ័ត្ន', 'ស្រីពៅ']
    khmer_last_names = ['ឈឿន', 'សោម', 'សុខ', 'ជាតិ']
    return random.choice(khmer_first_names), random.choice(khmer_last_names)

def random_english_name():
    english_first_names = ['John', 'Jane', 'Alex', 'Emily']
    english_last_names = ['Smith', 'Johnson', 'Brown', 'Lee']
    return random.choice(english_first_names), random.choice(english_last_names)

def random_korean_name():
    korean_first_names = ['지수', '민호', '현', '수진']
    korean_last_names = ['김', '박', '이', '최']
    return random.choice(korean_first_names), random.choice(korean_last_names)

def random_thai_name():
    thai_first_names = ['สมชาย', 'สุดา', 'นิรันดร์', 'อนงค์']
    thai_last_names = ['ชัย', 'พันธ์', 'ลิ้ม', 'จันทร์']
    return random.choice(thai_first_names), random.choice(thai_last_names)

def random_vietnamese_name():
    vietnamese_first_names = ['Anh', 'Hương', 'Nam', 'Linh']
    vietnamese_last_names = ['Nguyễn', 'Trần', 'Lê', 'Phạm']
    return random.choice(vietnamese_first_names), random.choice(vietnamese_last_names)

def random_japanese_name():
    japanese_first_names = ['Hiroshi', 'Yuki', 'Aiko', 'Ken']
    japanese_last_names = ['Tanaka', 'Yamamoto', 'Sato', 'Suzuki']
    return random.choice(japanese_first_names), random.choice(japanese_last_names)

def get_name_by_language_and_country(language, country):
    if language == "Khmer":
        return random_khmer_name()
    elif language == "Thai":
        return random_thai_name()
    elif language == "English":
        return random_english_name()
    elif language == "Korean":
        return random_korean_name()
    elif language == "Vietnamese":
        return random_vietnamese_name()
    elif language == "Japanese":
        return random_japanese_name()
    return "Unknown", "Unknown"

class WorkerThread(QThread):
    result_signal = pyqtSignal(str)
    table_row_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, country, language, mode, count):
        super().__init__()
        self.country = country
        self.language = language
        self.mode = mode
        self.count = count
        self.running = True

    def run(self):
        if self.language == "Generate Phone All":
            countries = ["KH", "TH", "US", "VN", "JP"]
            for _ in range(self.count):
                if not self.running:
                    break
                country = random.choice(countries)
                phone = generate_and_validate_phone(country)
                if not phone:
                    self.result_signal.emit(f"❌ Invalid phone for {country}")
                    continue
                self.result_signal.emit(f"✅ {country}: {phone}")
                self.table_row_signal.emit("", phone)  # Empty name for generate_phone_all
                with file_lock:
                    with open(os.path.join(output_dir, f"{country}_phones.txt"), mode="a", encoding="utf-8") as f:
                        f.write(phone + "\n")
        else:
            for _ in range(self.count):
                if not self.running:
                    break
                phone = generate_and_validate_phone(self.country)
                if not phone:
                    self.result_signal.emit(f"❌ Invalid phone for {self.country}")
                    continue

                if self.mode == "Auto":
                    if self.country == "KH":
                        first, last = random_khmer_name()
                    elif self.country == "TH":
                        first, last = random_thai_name()
                    elif self.country == "US":
                        first, last = random_english_name()
                    elif self.country == "VN":
                        first, last = random_vietnamese_name()
                    elif self.country == "JP":
                        first, last = random_japanese_name()
                    else:
                        first, last = "Unknown", "Unknown"
                else:
                    first, last = get_name_by_language_and_country(self.language, self.country)

                full_name = f"{first} {last}"
                line = f"{full_name} - {phone}"
                self.result_signal.emit(f"✅ {line}")
                self.table_row_signal.emit(full_name, phone)
                with file_lock:
                    with open(os.path.join(output_dir, f"{self.country}_phones.txt"), mode="a", encoding="utf-8") as f:
                        f.write(line + "\n")
        self.finished_signal.emit()

class PhoneGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phone Generator")
        self.setGeometry(100, 100, 600, 450)
        self.generated_data = []

        # UI Elements
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Auto", "All"])
        self.mode_combo.currentIndexChanged.connect(self.mode_changed)

        self.countries = QComboBox()
        self.countries.addItems(["KH", "TH", "US", "VN", "JP"])

        self.Get_names = QComboBox()
        self.Get_names.addItems([
            "Khmer", "Thai", "English", "Korean",
            "Vietnamese", "Japanese", "Generate Phone All"
        ])

        self.get_SpinBox_numbers = QSpinBox()
        self.get_SpinBox_numbers.setRange(1, 10000)
        self.get_SpinBox_numbers.setValue(10)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear)
        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.export_button = QPushButton("Export Excel")
        self.export_button.clicked.connect(self.export_to_excel)
        self.txt_button = QPushButton("Export TXT")
        self.txt_button.clicked.connect(self.export_to_txt)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Name", "Phone"])
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 200)  # Adjust Name column width
        self.table.setColumnWidth(1, 150)  # Adjust Phone column width

        self.show_hide_combo = QComboBox()
        self.show_hide_combo.addItems(["Hide All", "Show All"])
        self.show_hide_combo.currentIndexChanged.connect(self.show_hide_result_box)

        self.show_hide_ = QComboBox()
        self.show_hide_.addItems(["Hide", "Show"])
        self.show_hide_.currentIndexChanged.connect(self.show_hide)

        # Layouts
        Row1 = QHBoxLayout()
        Row1.addWidget(self.mode_combo)
        Row1.addWidget(self.countries)

        Row2 = QHBoxLayout()
        Row2.addWidget(self.Get_names)
        Row2.addWidget(self.get_SpinBox_numbers)
        Row2.addWidget(self.show_hide_)

        Row3 = QHBoxLayout()
        Row3.addWidget(self.start_button)
        Row3.addWidget(self.stop_button)
        Row3.addWidget(self.clear_button)

        Row4 = QHBoxLayout()
        Row4.addWidget(self.show_hide_combo)

        Row5 = QHBoxLayout()
        Row5.addWidget(self.copy_button)
        Row5.addWidget(self.export_button)
        Row5.addWidget(self.txt_button)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(Row4)
        main_layout.addLayout(Row1)
        main_layout.addLayout(Row2)
        main_layout.addWidget(self.result_box)
        main_layout.addWidget(self.table)
        main_layout.addLayout(Row3)
        main_layout.addLayout(Row5)
        self.setLayout(main_layout)

        self.show_hide_combo.setCurrentText("Hide All")
        self.show_hide_result_box()
        self.show_hide_.setCurrentText("Hide")
        self.show_hide()
        self.worker_thread = None

    def show_hide(self):
        action = self.show_hide_.currentText()
        if action == "Hide":
            self.result_box.hide()
        elif action == "Show":
            self.result_box.show()

    def show_hide_result_box(self):
        action = self.show_hide_combo.currentText()
        if action == "Hide All":
            self.mode_combo.hide()
            self.countries.hide()
            self.Get_names.hide()
            self.get_SpinBox_numbers.hide()
            self.start_button.hide()
            self.stop_button.hide()
            self.clear_button.hide()
            self.copy_button.hide()
            self.export_button.hide()
            self.txt_button.hide()
            self.result_box.hide()
            self.show_hide_.hide()
            self.table.hide()
        elif action == "Show All":
            self.mode_combo.show()
            self.countries.show()
            self.Get_names.show()
            self.get_SpinBox_numbers.show()
            self.start_button.show()
            self.stop_button.show()
            self.clear_button.show()
            self.copy_button.show()
            self.export_button.show()
            self.txt_button.show()
            self.table.show()
            self.show_hide_.show()

    def mode_changed(self):
        self.Get_names.setEnabled(self.mode_combo.currentText() != "Auto")

    def start(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.append_result("⚠️ Generation already in progress.")
            return
        self.result_box.clear()
        self.generated_data.clear()
        self.table.setRowCount(0)

        selected_country = self.countries.currentText()
        selected_language = self.Get_names.currentText()
        mode = self.mode_combo.currentText()
        count = self.get_SpinBox_numbers.value()

        self.worker_thread = WorkerThread(selected_country, selected_language, mode, count)
        self.worker_thread.result_signal.connect(self.append_result)
        self.worker_thread.table_row_signal.connect(self.add_table_row)
        self.worker_thread.finished_signal.connect(self.on_worker_finished)
        self.worker_thread.start()

    def stop(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.running = False
            self.append_result("⏹️ Stopped by user")
        else:
            self.append_result("⚠️ No generation in progress")

    def clear(self):
        self.result_box.clear()
        self.generated_data.clear()
        self.table.setRowCount(0)
        self.append_result("🗑️ Cleared results")

    def append_result(self, text):
        self.result_box.append(text)

    def add_table_row(self, name, phone):
        self.generated_data.append((name, phone))
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)
        self.table.setItem(row_pos, 0, QTableWidgetItem(name))
        self.table.setItem(row_pos, 1, QTableWidgetItem(phone))

    def on_worker_finished(self):
        self.worker_thread = None
        self.append_result("✅ Generation completed")

    def copy_to_clipboard(self):
        if not self.result_box.toPlainText():
            self.append_result("⚠️ Nothing to copy.")
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_box.toPlainText())
        self.append_result("📋 Copied to clipboard!")

    def export_to_excel(self):
        if not self.generated_data:
            self.append_result("⚠️ No data to export.")
            return
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", os.path.join(output_dir, "exported_phones.xlsx"), "Excel Files (*.xlsx)")
            if file_path:
                df = pd.DataFrame(self.generated_data, columns=["Name", "Phone"])
                df.to_excel(file_path, index=False)
                self.append_result(f"📁 Exported to: {file_path}")
        except Exception as e:
            self.append_result(f"❌ Export failed: {str(e)}")

    def export_to_txt(self):
        if not self.generated_data:
            self.append_result("⚠️ No data to export.")
            return
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save TXT File", os.path.join(output_dir, f"{self.countries.currentText()}_phones.txt"), "Text Files (*.txt)")
            if file_path:
                with file_lock:
                    with open(file_path, mode="w", encoding="utf-8") as f:
                        for name, phone in self.generated_data:
                            f.write(f"{name} - {phone}\n")
                self.append_result(f"📁 Exported to: {file_path}")
        except Exception as e:
            self.append_result(f"❌ TXT Export failed: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhoneGeneratorApp()
    window.show()
    sys.exit(app.exec_())
