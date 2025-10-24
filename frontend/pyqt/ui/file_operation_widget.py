from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QFileDialog, QProgressBar,
                             QTextEdit, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from utils.config import BUTTON_STYLE, DANGER_BUTTON_STYLE
from utils.helpers import show_message, get_file_info, format_file_size

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
        
        self.decrypt_btn = QPushButton("🔓 Giải mã File")
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
    
    def select_file(self):
        """Chọn file để xử lý"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file để mã hóa/giải mã",
            "",
            "All Files (*.*)"
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
        """Xóa file đã chọn"""
        self.selected_file = None
        self.file_info_label.setText("Chưa chọn file nào")
        self.clear_file_btn.setEnabled(False)
        self.encrypt_btn.setEnabled(False)
        self.decrypt_btn.setEnabled(False)
        self.add_log("Đã xóa file đã chọn")
    
    def encrypt_file(self):
        """Mã hóa file"""
        if not self.selected_file:
            show_message(self, "Lỗi", "Vui lòng chọn file trước", "error")
            return
        
        self.start_operation("Đang mã hóa file...")
        
        try:
            result, status_code = self.api_service.encrypt_file(self.selected_file)
            
            if status_code == 200:
                self.add_log("✅ Mã hóa file thành công")
                show_message(self, "Thành công", "File đã được mã hóa thành công!")
                
                # Có thể lưu file đã mã hóa
                if 'encrypted_file_path' in result:
                    save_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Lưu file đã mã hóa",
                        f"{self.selected_file}.encrypted",
                        "Encrypted Files (*.encrypted)"
                    )
                    if save_path:
                        self.add_log(f"File đã mã hóa được lưu tại: {save_path}")
            else:
                error_msg = result.get('message', 'Mã hóa thất bại')
                self.add_log(f"❌ Lỗi mã hóa: {error_msg}")
                show_message(self, "Lỗi", error_msg, "error")
                
        except Exception as e:
            self.add_log(f"❌ Lỗi: {str(e)}")
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")
        
        finally:
            self.finish_operation()
    
    def decrypt_file(self):
        """Giải mã file"""
        if not self.selected_file:
            show_message(self, "Lỗi", "Vui lòng chọn file trước", "error")
            return
        
        self.start_operation("Đang giải mã file...")
        
        try:
            result, status_code = self.api_service.decrypt_file(self.selected_file)
            
            if status_code == 200:
                self.add_log("✅ Giải mã file thành công")
                show_message(self, "Thành công", "File đã được giải mã thành công!")
                
                # Có thể lưu file đã giải mã
                if 'decrypted_file_path' in result:
                    save_path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Lưu file đã giải mã",
                        f"{self.selected_file}.decrypted",
                        "All Files (*.*)"
                    )
                    if save_path:
                        self.add_log(f"File đã giải mã được lưu tại: {save_path}")
            else:
                error_msg = result.get('message', 'Giải mã thất bại')
                self.add_log(f"❌ Lỗi giải mã: {error_msg}")
                show_message(self, "Lỗi", error_msg, "error")
                
        except Exception as e:
            self.add_log(f"❌ Lỗi: {str(e)}")
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")
        
        finally:
            self.finish_operation()
    
    def start_operation(self, message):
        """Bắt đầu thao tác - hiển thị progress"""
        self.status_label.setText(message)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.encrypt_btn.setEnabled(False)
        self.decrypt_btn.setEnabled(False)
        self.select_file_btn.setEnabled(False)
    
    def finish_operation(self):
        """Kết thúc thao tác - ẩn progress"""
        self.status_label.setText("Sẵn sàng")
        self.progress_bar.setVisible(False)
        self.encrypt_btn.setEnabled(True)
        self.decrypt_btn.setEnabled(True)
        self.select_file_btn.setEnabled(True)
    
    def add_log(self, message):
        """Thêm dòng log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def clear_log(self):
        """Xóa nhật ký"""
        self.log_text.clear()
        self.add_log("Nhật ký đã được xóa")