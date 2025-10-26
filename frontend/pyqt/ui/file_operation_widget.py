
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QFileDialog, QProgressBar,
                             QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt
from utils.config import BUTTON_STYLE, DANGER_BUTTON_STYLE
from utils.helpers import CryptoUtils, show_message, get_file_info, format_file_size
import os
import shutil
import requests
import base64
import tempfile
import time


class FileOperationWidget(QWidget):
    def __init__(self, api_service):
        super().__init__()
        self.api_service = api_service
        self.selected_file = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Mã hóa / Giải mã File")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # File selection section
        file_section = QGroupBox("Chọn File")
        file_layout = QVBoxLayout()
        
        # File info display
        self.file_info_label = QLabel("Chưa chọn file nào")
        self.file_info_label.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px; background-color: #f9f9f9;")
        file_layout.addWidget(self.file_info_label)
        
        # File selection buttons
        file_btn_layout = QHBoxLayout()
        
        self.select_file_btn = QPushButton("Chọn File")
        self.select_file_btn.setStyleSheet(BUTTON_STYLE)
        self.select_file_btn.clicked.connect(self.select_file)
        
        self.clear_file_btn = QPushButton("Xóa")
        self.clear_file_btn.setStyleSheet(DANGER_BUTTON_STYLE)
        self.clear_file_btn.clicked.connect(self.clear_file)
        self.clear_file_btn.setEnabled(False)
        
        file_btn_layout.addWidget(self.select_file_btn)
        file_btn_layout.addWidget(self.clear_file_btn)
        file_layout.addLayout(file_btn_layout)
        
        file_section.setLayout(file_layout)
        layout.addWidget(file_section)
        
        # Operation buttons
        operation_section = QGroupBox("Thao tác")
        operation_layout = QGridLayout()
        
        self.encrypt_btn = QPushButton("Mã hóa File")
        self.encrypt_btn.setStyleSheet(BUTTON_STYLE)
        self.encrypt_btn.clicked.connect(self.encrypt_file)
        self.encrypt_btn.setEnabled(False)
        
        self.decrypt_btn = QPushButton("Giải mã File")
        self.decrypt_btn.setStyleSheet(BUTTON_STYLE)
        self.decrypt_btn.clicked.connect(self.decrypt_file)
        self.decrypt_btn.setEnabled(False)
        
        operation_layout.addWidget(self.encrypt_btn, 0, 0)
        operation_layout.addWidget(self.decrypt_btn, 0, 1)
        
        operation_section.setLayout(operation_layout)
        layout.addWidget(operation_section)
        
        # Progress section
        progress_section = QGroupBox("Tiến trình")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        progress_section.setLayout(progress_layout)
        layout.addWidget(progress_section)
        
        # Log section
        log_section = QGroupBox("Nhật ký")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ccc;")
        log_layout.addWidget(self.log_text)
        
        clear_log_btn = QPushButton("Xóa nhật ký")
        clear_log_btn.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_btn)
        
        log_section.setLayout(log_layout)
        layout.addWidget(log_section)
        
        self.setLayout(layout)
        
        # Add initial log
        self.add_log("Ứng dụng khởi động thành công")

    def add_log(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def clear_log(self):
        self.log_text.clear()
        self.add_log("Đã xóa nhật ký")

    def start_operation(self, status_text="Đang xử lý..."):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Vô hạn
        self.status_label.setText(status_text)
        self.encrypt_btn.setEnabled(False)
        self.decrypt_btn.setEnabled(False)

    def finish_operation(self):
        self.progress_bar.setVisible(False)
        self.status_label.setText("Sẵn sàng")
        if self.selected_file:
            self.encrypt_btn.setEnabled(True)
            self.decrypt_btn.setEnabled(True)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file để mã hóa/giải mã", "", "All Files (*.*)"
        )
        if file_path:
            self.selected_file = file_path
            file_info = get_file_info(file_path)
            if file_info:
                info_text = f"""
                <b>Tên file:</b> {file_info['name']}<br>
                <b>Kích thước:</b> {format_file_size(file_info['size'])}<br>
                <b>Loại file:</b> .{file_info['extension']}<br>
                <b>Đường dẫn:</b> {file_info['path']}
                """
                self.file_info_label.setText(info_text)
                self.clear_file_btn.setEnabled(True)
                self.encrypt_btn.setEnabled(True)
                self.decrypt_btn.setEnabled(True)
                self.add_log(f"Đã chọn file: {file_info['name']}")
            else:
                show_message(self, "Lỗi", "Không thể đọc thông tin file", "error")

    def clear_file(self):
        self.selected_file = None
        self.file_info_label.setText("Chưa chọn file nào")
        self.clear_file_btn.setEnabled(False)
        self.encrypt_btn.setEnabled(False)
        self.decrypt_btn.setEnabled(False)
        self.add_log("Đã xóa file đã chọn")

    def encrypt_file(self):
        if not self.selected_file:
            return show_message(self, "Lỗi", "Chọn file trước", "error")

        self.start_operation("Đang mã hóa...")

        try:
            # 1. Lấy public key
            keys, status = self.api_service.get_user_keys()
            if status != 200 or keys.get('error') != 0:
                raise ValueError("Không lấy được public key")
            public_key = keys['data']['publicKey']

            # 2. Tạo AES key + mã hóa file -> write to a temp file to avoid locking original dir
            aes_key_b64 = CryptoUtils.generate_aes_key()
            fd, enc_path = tempfile.mkstemp(suffix='.enc')
            os.close(fd)
            try:
                CryptoUtils.encrypt_file(self.selected_file, enc_path, aes_key_b64)
            except Exception:
                # If encryption failed, ensure temp file removed and re-raise
                if os.path.exists(enc_path):
                    try:
                        os.remove(enc_path)
                    except Exception:
                        pass
                raise

            # 3. Mã hóa AES key bằng RSA
            encrypted_aes_key_b64 = CryptoUtils.wrap_aes_key_with_rsa(aes_key_b64, public_key)

            # 4. Gửi metadata lên /file/upload
            filename = os.path.basename(self.selected_file)
            payload = {
                'filename': filename,
                'filePath': enc_path,  # include encrypted file path so backend can record it
                'aesKey': aes_key_b64  # backend dùng aesKey
            }
            response = requests.post(
                f'{self.api_service.base_url}/file/upload',
                json=payload,
                headers=self.api_service.get_headers()
            )
            result, status_code = response.json(), response.status_code
            if status_code not in (200, 201):
                raise ValueError(result.get('message', 'Upload metadata thất bại'))

            # 5. Lưu file + key local
            save_dir = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu")
            if not save_dir:
                raise ValueError("Phải chọn nơi lưu")

            final_enc = os.path.join(save_dir, filename + ".enc")
            final_key = final_enc + ".key"

            # Try to copy the temp encrypted file to final location with retries to avoid
            # transient Windows file locks (WinError 32). If copying fails permanently,
            # raise and cleanup temp file.
            copy_attempts = 5
            for attempt in range(1, copy_attempts + 1):
                try:
                    shutil.copy2(enc_path, final_enc)
                    break
                except PermissionError as e:
                    # WinError 32 -> file locked, wait and retry
                    if attempt == copy_attempts:
                        raise
                    time.sleep(0.2 * attempt)

            with open(final_key, 'w', encoding='utf-8') as f:
                f.write(encrypted_aes_key_b64)

            try:
                os.remove(enc_path)
            except Exception:
                # If removal fails, don't block success — just log and continue
                self.add_log(f"Không xóa được file tạm: {enc_path}")

            # 6. Thông báo
            msg = f"""
            <b>Mã hóa thành công!</b><br><br>
            <b>File:</b> <code>{final_enc}</code><br>
            <b>Key:</b> <code>{final_key}</code><br><br>
            <i>Lưu cả 2 file này an toàn!</i>
            """
            show_message(self, "Thành công", msg, "info")
            self.add_log("Mã hóa & lưu local thành công")

        except Exception as e:
            self.add_log(f"Lỗi: {e}")
            show_message(self, "Lỗi", str(e), "error")
        finally:
            self.finish_operation()

    def decrypt_file(self):
        if not self.selected_file or not self.selected_file.endswith('.enc'):
            return show_message(self, "Lỗi", "Chọn file .enc", "error")

        key_path, _ = QFileDialog.getOpenFileName(self, "Chọn file key", "", "Key File (*.key)")
        if not key_path:
            return

        self.start_operation("Đang giải mã...")

        try:
            # 1. Lấy private key
            keys, status = self.api_service.get_user_keys()
            if status != 200 or keys.get('error') != 0:
                raise ValueError("Không lấy được private key")
            private_key = keys['data']['privateKey']

            # 2. Đọc encrypted key từ file .key
            encrypted_aes_key_b64 = open(key_path, 'r', encoding='utf-8').read().strip()

            # 3. Giải mã AES key bằng RSA
            aes_key_b64 = CryptoUtils.unwrap_aes_key_with_rsa(encrypted_aes_key_b64, private_key)

            # 4. Giải mã file
            save_path, _ = QFileDialog.getSaveFileName(
                self, "Lưu file gốc", os.path.basename(self.selected_file).replace('.enc', ''), "All Files (*)"
            )
            if not save_path:
                return

            CryptoUtils.decrypt_file(self.selected_file, save_path, aes_key_b64)

            show_message(self, "Thành công", f"Giải mã thành công!\nLưu tại: {save_path}")
            self.add_log("Giải mã thành công")

        except Exception as e:
            self.add_log(f"Lỗi: {e}")
            show_message(self, "Lỗi", str(e), "error")
        finally:
            self.finish_operation()