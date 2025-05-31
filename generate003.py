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

class Generate:
    def __init__(self):
        self.country_phone_prefixes = {
            "KH": ['+85596', '+85597', '+85588', '+85571'],
            "TH": ['+6691', '+6683', '+6686', '+6687'],
            "US": ['+1'],
            "VN": ['+8491', '+8490', '+8488', '+8493'],
            "JP": ['+81']
        }
        self.name_data = {
            "Khmer": {
                "first_names": ['សុភា', 'ចាន់ដា', 'រ័ត្ន', 'ស្រីពៅ'],
                "last_names": ['ឈឿន', 'សោម', 'សុខ', 'ជាតិ']
            },
            "Thai": {
                "first_names": ['สมชาย', 'สุดา', 'นิรันดร์', 'อนงค์'],
                "last_names": ['ชัย', 'พันธ์', 'ลิ้ม', 'จันทร์']
            },
            "English": {
                "first_names": ['John', 'Jane', 'Alex', 'Emily'],
                "last_names": ['Smith', 'Johnson', 'Brown', 'Lee']
            },
            "Korean": {
                "first_names": ['지수', '민호', '현', '수진'],
                "last_names": ['김', '박', '이', '최']
            },
            "Vietnamese": {
                "first_names": ['Anh', 'Hương', 'Nam', 'Linh'],
                "last_names": ['Nguyễn', 'Trần', 'Lê', 'Phạm']
            },
            "Japanese": {
                "first_names": ['Hiroshi', 'Yuki', 'Aiko', 'Ken'],
                "last_names": ['Tanaka', 'Yamamoto', 'Sato', 'Suzuki']
            }
        }

    def generate_and_validate_phone(self, country):
        if country not in self.country_phone_prefixes:
            return None
        prefixes = self.country_phone_prefixes[country]
        if country == "US":
            phone = prefixes[0] + str(random.randint(2000000000, 9999999999))
        elif country == "JP":
            phone = prefixes[0] + str(random.randint(70, 90)) + str(random.randint(10000000, 99999999))
        else:
            phone = random.choice(prefixes) + str(random.randint(1000000, 9999999))
        try:
            parsed = phonenumbers.parse(phone, None)
            if phonenumbers.is_valid_number(parsed):
                return phone
            return None
        except NumberParseException:
            return None

    def get_name(self, language, country):
        if language not in self.name_data:
            return "Unknown", "Unknown"
        first_name = random.choice(self.name_data[language]["first_names"])
        last_name = random.choice(self.name_data[language]["last_names"])
        return first_name, last_name

    def get_name_by_country(self, country):
        country_language_map = {
            "KH": "Khmer",
            "TH": "Thai",
            "US": "English",
            "VN": "Vietnamese",
            "JP": "Japanese"
        }
        language = country_language_map.get(country, "English")
        return self.get_name(language, country)

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
        self.generator = Generate()

    def run(self):
        if self.language == "Generate Phone All":
            countries = ["KH", "TH", "US", "VN", "JP"]
            for _ in range(self.count):
                if not self.running:
                    break
                country = random.choice(countries)
                phone = self.generator.generate_and_validate_phone(country)
                if not phone:
                    self.result_signal.emit(f"❌ Invalid phone for {country}")
                    continue
                self.result_signal.emit(f"✅ {country}: {phone}")
                self.table_row_signal.emit("", phone)
                with file_lock:
                    with open(os.path.join(output_dir, f"{country}_phones.txt"), mode="a", encoding="utf-8") as f:
                        f.write(phone + "\n")
        else:
            for _ in range(self.count):
                if not self.running:
                    break
                phone = self.generator.generate_and_validate_phone(self.country)
                if not phone:
                    self.result_signal.emit(f"❌ Invalid phone for {self.country}")
                    continue

                if self.mode == "Auto":
                    first, last = self.generator.get_name_by_country(self.country)
                else:
                    first, last = self.generator.get_name(self.language, self.country)

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
        self.generated()



        
    def generated(self):

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
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 150)



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


        Row5 = QHBoxLayout()
        Row5.addWidget(self.copy_button)
        Row5.addWidget(self.export_button)
        Row5.addWidget(self.txt_button)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(Row1)
        main_layout.addLayout(Row2)
        main_layout.addWidget(self.result_box)
        main_layout.addWidget(self.table)
        main_layout.addLayout(Row3)
        main_layout.addLayout(Row5)
        self.setLayout(main_layout)
        self.mode_changed()

        self.show_hide_.setCurrentText("Hide")
        self.show_hide()
        self.worker_thread = None

    def show_hide(self):
        action = self.show_hide_.currentText()
        if action == "Hide":
            self.result_box.hide()
        elif action == "Show":
            self.result_box.show()


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
