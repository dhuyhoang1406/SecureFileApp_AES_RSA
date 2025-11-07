
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QFileDialog, QProgressBar,
                             QTextEdit, QGroupBox, QLineEdit, QInputDialog, 
                             QDialog, QListWidget)
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
        
        self.encrypt_btn = QPushButton("🔒 Mã hóa File")
        self.encrypt_btn.setStyleSheet(BUTTON_STYLE)
        self.encrypt_btn.clicked.connect(self.encrypt_file)
        self.encrypt_btn.setEnabled(False)
        
        self.decrypt_btn = QPushButton("🔓 Giải mã Cá nhân")
        self.decrypt_btn.setStyleSheet(BUTTON_STYLE)
        self.decrypt_btn.clicked.connect(self.decrypt_file)
        self.decrypt_btn.setEnabled(False)
        
        self.share_btn = QPushButton("🤝 Share File")
        self.share_btn.setStyleSheet(BUTTON_STYLE)
        self.share_btn.clicked.connect(self.share_file_ui)
        self.share_btn.setEnabled(False)
        
        self.decrypt_shared_btn = QPushButton("👥 Giải mã Bạn bè")
        self.decrypt_shared_btn.setStyleSheet(BUTTON_STYLE)
        self.decrypt_shared_btn.clicked.connect(self.decrypt_shared_file)
        # Nút này không phụ thuộc vào file được chọn vì nó tự chọn file từ server
        
        operation_layout.addWidget(self.encrypt_btn, 0, 0)
        operation_layout.addWidget(self.decrypt_btn, 0, 1)
        operation_layout.addWidget(self.share_btn, 1, 0)
        operation_layout.addWidget(self.decrypt_shared_btn, 1, 1)
        
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
                self.share_btn.setEnabled(True)
                self.add_log(f"Đã chọn file: {file_info['name']}")
            else:
                show_message(self, "Lỗi", "Không thể đọc thông tin file", "error")

    def clear_file(self):
        self.selected_file = None
        self.file_info_label.setText("Chưa chọn file nào")
        self.clear_file_btn.setEnabled(False)
        self.encrypt_btn.setEnabled(False)
        self.decrypt_btn.setEnabled(False)
        self.share_btn.setEnabled(False)
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
                'aesKey': encrypted_aes_key_b64  # ✅ GỬI WRAPPED KEY (đã mã hóa bằng RSA)
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

        # YÊU CẦU PASSWORD để lấy private key
        password, ok = QInputDialog.getText(
            self, 
            "Xác nhận mật khẩu", 
            "Nhập mật khẩu để lấy Private Key cho giải mã:",
            QLineEdit.Password
        )
        
        if not ok or not password:
            return

        self.start_operation("Đang giải mã...")

        try:
            # 1. Lấy private key với password verification
            keys, status = self.api_service.get_private_key(password)
            if status != 200 or keys.get('error') != 0:
                if status == 401:
                    raise ValueError("Mật khẩu không chính xác!")
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

    def share_file_ui(self):
        """
        Share file đã chọn cho người khác
        
        Yêu cầu: Phải chọn file .enc trước khi click Share
        
        Luồng:
        1. Kiểm tra file đã chọn (self.selected_file phải là .enc)
        2. Tìm file tương ứng trong database (match tên)
        3. Nhập email người nhận
        4. Gọi API share
        """
        try:
            # 1. Kiểm tra đã chọn file chưa
            if not self.selected_file:
                show_message(self, "Lỗi", "Vui lòng chọn file .enc trước khi share", "warning")
                return
            
            # 2. Kiểm tra file có phải .enc không
            if not self.selected_file.endswith('.enc'):
                show_message(self, "Lỗi", "Chỉ có thể share file .enc (file đã mã hóa)", "warning")
                return
            
            # 3. Lấy tên file gốc từ file .enc
            # VD: report.docx.enc → report.docx
            selected_filename = os.path.basename(self.selected_file).replace('.enc', '')
            self.add_log(f"Chuẩn bị share file: {selected_filename}")
            
            # 4. Lấy danh sách file từ server để tìm file ID
            response, status = self.api_service.get_user_files()
            if status != 200 or response.get('error') != 0:
                show_message(self, "Lỗi", "Không thể lấy danh sách file từ server", "error")
                return
            
            files = response.get('data', [])
            if not files:
                show_message(self, "Lỗi", "Bạn chưa có file nào trên server.\nHãy mã hóa và upload file trước!", "warning")
                return
            
            # 5. Tìm file tương ứng trong database
            matched_file = None
            for file in files:
                if file['filename'] == selected_filename:
                    matched_file = file
                    break
            
            if not matched_file:
                show_message(
                    self, 
                    "Lỗi", 
                    f"Không tìm thấy file '{selected_filename}' trên server.\n\n"
                    f"Có thể file này chưa được mã hóa và upload.\n"
                    f"Vui lòng chọn file .enc khác hoặc mã hóa file này trước.",
                    "warning"
                )
                return
            
            file_id = matched_file['id']
            self.add_log(f"Tìm thấy file trên server: ID={file_id}, filename={selected_filename}")
            
            # 6. Dialog nhập email người nhận
            dialog = QDialog(self)
            dialog.setWindowTitle("Chia sẻ File")
            dialog.setMinimumWidth(400)
            dialog.setMinimumHeight(200)
            
            layout = QVBoxLayout()
            
            # Hiển thị thông tin file
            info_label = QLabel(
                f"<b>File sẽ share:</b> {selected_filename}<br>"
                f"<b>File ID:</b> {file_id}"
            )
            layout.addWidget(info_label)
            
            # Input email
            email_label = QLabel("Email người nhận:")
            layout.addWidget(email_label)
            
            email_input = QLineEdit()
            email_input.setPlaceholderText("Nhập email người nhận...")
            layout.addWidget(email_input)
            
            # Buttons
            button_layout = QHBoxLayout()
            share_btn = QPushButton("Chia sẻ")
            cancel_btn = QPushButton("Hủy")
            button_layout.addWidget(share_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # 7. Xử lý khi click share
            def on_share():
                recipient_email = email_input.text().strip()
                if not recipient_email:
                    show_message(self, "Lỗi", "Vui lòng nhập email người nhận", "warning")
                    return
                
                # Gọi API share
                self.add_log(f"Đang share file ID {file_id} cho {recipient_email}...")
                result, status = self.api_service.share_file(file_id, recipient_email)
                
                if status != 200 or result.get('error') != 0:
                    error_msg = result.get('message', 'Không thể chia sẻ file')
                    show_message(self, "Lỗi", error_msg, "error")
                    self.add_log(f"Share thất bại: {error_msg}")
                    return
                
                # ✅ TẠO FILE .enc.key TỪ WRAPPED KEY CỦA RECIPIENT
                # Backend đã re-wrap AES key bằng public key của recipient
                # Wrapped key này nằm trong sharedFile.aesKey
                shared_file = result.get('sharedFile', {})
                if not shared_file:
                    show_message(self, "Lỗi", "Không nhận được thông tin shared file từ server", "error")
                    self.add_log(f"DEBUG: Backend response = {result}")
                    return
                
                # Lấy wrapped key (đã được mã hóa bằng public key của recipient)
                wrapped_key_for_recipient_b64 = shared_file.get('aesKey')
                if not wrapped_key_for_recipient_b64:
                    show_message(self, "Lỗi", "Không có wrapped key trong shared file", "error")
                    return
                
                # Tạo đường dẫn file .enc.key (cùng thư mục với .enc)
                key_file_path = self.selected_file + '.key'
                
                # Ghi wrapped key vào file .enc.key (BINARY, không phải base64 text)
                self.add_log(f"Đang tạo file .enc.key tại {key_file_path}...")
                try:
                    import base64
                    wrapped_key_bytes = base64.b64decode(wrapped_key_for_recipient_b64)
                    with open(key_file_path, 'wb') as f:
                        f.write(wrapped_key_bytes)
                    self.add_log(f"✅ Đã tạo file .enc.key ({len(wrapped_key_bytes)} bytes)")
                except Exception as e:
                    show_message(self, "Lỗi", f"Không thể tạo file .enc.key:\n{str(e)}", "error")
                    self.add_log(f"Lỗi tạo .enc.key: {e}")
                    return
                
                show_message(
                    self, 
                    "Thành công", 
                    f"✅ Đã chia sẻ file cho {recipient_email}\n\n"
                    f"� Đã tạo file key: {os.path.basename(key_file_path)}\n\n"
                    f"📝 Lưu ý: Gửi CẢ HAI FILE cho người nhận:\n"
                    f"   1️⃣ {os.path.basename(self.selected_file)}\n"
                    f"   2️⃣ {os.path.basename(key_file_path)}\n\n"
                )
                self.add_log(f"✅ Đã share file và tạo .enc.key thành công!")
                dialog.accept()
            
            share_btn.clicked.connect(on_share)
            cancel_btn.clicked.connect(dialog.reject)
            
            # 8. Hiển thị dialog
            dialog.exec_()
            
        except Exception as e:
            self.add_log(f"Lỗi share file: {e}")
            show_message(self, "Lỗi", str(e), "error")

    def decrypt_shared_file(self):
        """
        Giải mã file được chia sẻ từ bạn bè (LUỒNG MỚI - Đơn giản hơn)
        
        Yêu cầu:
        - Người dùng đã nhận 2 file từ bạn: file.enc và file.enc.key
        
        Luồng:
        1. Chọn file .enc từ local
        2. Tự động tìm file .enc.key cùng thư mục
        3. Nhập password để lấy private key
        4. Unwrap AES key từ file .enc.key
        5. Giải mã file .enc
        """
        try:
            self.add_log("=== Bắt đầu giải mã file bạn bè (Luồng mới) ===")
            
            # 1. Chọn file .enc từ local
            enc_file, _ = QFileDialog.getOpenFileName(
                self, 
                "Chọn file .enc đã nhận từ bạn bè", 
                "", 
                "Encrypted Files (*.enc);;All Files (*)"
            )
            if not enc_file:
                self.add_log("Đã hủy chọn file")
                return
            
            self.add_log(f"📁 Đã chọn file: {enc_file}")
            self.start_operation()
            
            # 2. Tìm file .enc.key cùng thư mục
            key_file = enc_file + '.key'
            if not os.path.exists(key_file):
                show_message(
                    self, 
                    "Lỗi", 
                    f"❌ Không tìm thấy file key!\n\n"
                    f"Tìm kiếm: {os.path.basename(key_file)}\n"
                    f"Tại: {os.path.dirname(key_file)}\n\n"
                    f"Đảm bảo bạn đã nhận CẢ HAI FILE:\n"
                    f"  • {os.path.basename(enc_file)}\n"
                    f"  • {os.path.basename(key_file)}",
                    "error"
                )
                self.finish_operation()
                return
            
            self.add_log(f"🔑 Tìm thấy file key: {key_file}")
            
            # 3. Yêu cầu password để lấy private key
            password, ok = QInputDialog.getText(
                self, 
                "Xác nhận", 
                "Nhập mật khẩu để giải mã:", 
                QLineEdit.Password
            )
            if not ok or not password:
                self.add_log("Đã hủy nhập password")
                self.finish_operation()
                return
            
            # 4. Lấy private key từ server
            self.add_log("Đang lấy private key...")
            keys, status = self.api_service.get_private_key(password)
            if status != 200 or keys.get('error') != 0:
                if status == 401:
                    show_message(self, "Lỗi", "❌ Mật khẩu không chính xác!", "error")
                else:
                    show_message(self, "Lỗi", "❌ Không lấy được private key", "error")
                self.finish_operation()
                return
            
            private_key = keys['data']['privateKey']
            self.add_log("✅ Đã lấy private key thành công")
            
            # 5. Đọc wrapped key từ file .enc.key
            self.add_log("Đang đọc file .enc.key...")
            with open(key_file, 'rb') as f:
                wrapped_key_bytes = f.read()
            
            # Chuyển sang base64 để unwrap
            import base64
            wrapped_key_b64 = base64.b64encode(wrapped_key_bytes).decode()
            self.add_log(f"Đã đọc {len(wrapped_key_bytes)} bytes từ file .enc.key")
            
            # 6. Unwrap AES key bằng RSA private key
            self.add_log("Đang unwrap AES key...")
            aes_key_b64 = CryptoUtils.unwrap_aes_key_with_rsa(wrapped_key_b64, private_key)
            self.add_log("✅ Unwrap AES key thành công")
            
            # 7. Kiểm tra độ dài AES key
            aes_key_bytes = base64.b64decode(aes_key_b64)
            self.add_log(f"DEBUG: AES key length = {len(aes_key_bytes)} bytes")
            self.add_log(f"DEBUG: AES key (hex) = {aes_key_bytes.hex()}")
            
            if len(aes_key_bytes) != 16:
                show_message(
                    self, 
                    "Lỗi", 
                    f"❌ AES key không hợp lệ!\n\n"
                    f"Độ dài: {len(aes_key_bytes)} bytes (cần 16 bytes)\n"
                    f"Key hex: {aes_key_bytes.hex()}\n\n"
                    f"File .enc.key có thể bị hỏng hoặc không đúng định dạng.",
                    "error"
                )
                self.finish_operation()
                return
            
            # 8. Chọn nơi lưu file đã giải mã
            original_name = os.path.basename(enc_file).replace('.enc', '')
            save_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Lưu file đã giải mã", 
                original_name, 
                "All Files (*)"
            )
            if not save_path:
                self.add_log("Đã hủy chọn nơi lưu")
                self.finish_operation()
                return
            
            # 9. Giải mã file
            self.add_log(f"Đang giải mã file...")
            CryptoUtils.decrypt_file(enc_file, save_path, aes_key_b64)
            
            show_message(
                self, 
                "Thành công", 
                f"✅ Giải mã file bạn bè thành công!\n\n"
                f"File gốc: {os.path.basename(enc_file)}\n"
                f"Đã lưu tại: {save_path}"
            )
            self.add_log(f"🎉 Giải mã thành công!")
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.add_log(f"❌ Lỗi giải mã file bạn bè:\n{error_detail}")
            show_message(self, "Lỗi", f"❌ {str(e)}", "error")
        finally:
            self.finish_operation()