from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QGroupBox,
                             QTextEdit, QMessageBox, QLineEdit, QInputDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import os
from utils.config import BUTTON_STYLE
from utils.helpers import show_message

class KeyManagementWidget(QWidget):
    def __init__(self, api_service):
        super().__init__()
        self.api_service = api_service
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Quản lý RSA Keys")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(header)
        
        # Key display section
        key_section = QGroupBox("RSA Keys của bạn")
        key_layout = QVBoxLayout()
        
        # Public key
        pub_label = QLabel("Public Key:")
        self.public_key_text = QTextEdit()
        self.public_key_text.setMaximumHeight(100)
        self.public_key_text.setReadOnly(True)
        self.public_key_text.setPlaceholderText("Public key sẽ hiển thị ở đây...")
        
        # Private key
        priv_label = QLabel("Private Key (nhấn nút bên dưới để hiển thị - yêu cầu password):")
        self.private_key_text = QTextEdit()
        self.private_key_text.setMaximumHeight(100)
        self.private_key_text.setReadOnly(True)
        self.private_key_text.setPlaceholderText("*** Private key được bảo vệ - nhấn 'Hiện Private Key' ***")
        
        key_layout.addWidget(pub_label)
        key_layout.addWidget(self.public_key_text)
        key_layout.addWidget(priv_label)
        key_layout.addWidget(self.private_key_text)
        
        key_section.setLayout(key_layout)
        layout.addWidget(key_section)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.load_keys_btn = QPushButton("Tải Public Key")
        self.load_keys_btn.setStyleSheet(BUTTON_STYLE)
        self.load_keys_btn.clicked.connect(self.load_user_keys)
        
        self.show_private_key_btn = QPushButton("Hiện Private Key")
        self.show_private_key_btn.setStyleSheet(BUTTON_STYLE)
        self.show_private_key_btn.clicked.connect(self.show_private_key)
        
        button_layout.addWidget(self.load_keys_btn)
        button_layout.addWidget(self.show_private_key_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_user_keys(self):
        """Tải PUBLIC KEY từ server (không cần password)"""
        try:
            result, status_code = self.api_service.get_user_keys()
            
            if status_code == 200 and result.get('error') == 0:
                keys = result.get('data', {})
                self.public_key_text.setText(keys.get('publicKey', ''))
                # KHÔNG hiển thị private key ở đây
                self.private_key_text.setPlaceholderText("*** Nhấn 'Hiện Private Key' để xem (yêu cầu password) ***")
                show_message(self, "Thành công", "Đã tải public key thành công!")
            else:
                error_msg = result.get('message', 'Không thể tải keys')
                show_message(self, "Lỗi", error_msg, "error")
                
        except Exception as e:
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")
    
    def show_private_key(self):
        """Hiển thị PRIVATE KEY - YÊU CẦU XÁC NHẬN PASSWORD"""
        # Yêu cầu nhập password
        password, ok = QInputDialog.getText(
            self, 
            "Xác nhận mật khẩu", 
            "Nhập mật khẩu của bạn để xem Private Key:",
            QLineEdit.Password
        )
        
        if not ok or not password:
            return
        
        try:
            result, status_code = self.api_service.get_private_key(password)
            
            if status_code == 200 and result.get('error') == 0:
                private_key = result.get('data', {}).get('privateKey', '')
                self.private_key_text.setText(private_key)
                show_message(self, "Thành công", "Đã hiển thị private key!")
            elif status_code == 401:
                show_message(self, "Lỗi", "Mật khẩu không chính xác!", "error")
            else:
                error_msg = result.get('message', 'Không thể lấy private key')
                show_message(self, "Lỗi", error_msg, "error")
                
        except Exception as e:
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")
    
    def generate_new_keys(self):
        """BỎ FUNCTION NÀY - Keys được tạo tự động khi register"""
        show_message(
            self, 
            "Thông báo", 
            "RSA keys được tạo tự động khi đăng ký.\nKhông cần tạo lại keys thủ công.",
            "info"
        )

class FileListWidget(QWidget):
    def __init__(self, api_service):
        super().__init__()
        self.api_service = api_service
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Danh sách File đã mã hóa")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(header)
        
        # File list
        list_section = QGroupBox("Files của bạn")
        list_layout = QVBoxLayout()
        
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(200)
        list_layout.addWidget(self.file_list)
        
        # Refresh button
        self.refresh_btn = QPushButton("Làm mới danh sách")
        self.refresh_btn.setStyleSheet(BUTTON_STYLE)
        self.refresh_btn.clicked.connect(self.refresh_file_list)
        list_layout.addWidget(self.refresh_btn)
        
        list_section.setLayout(list_layout)
        layout.addWidget(list_section)
        
        self.setLayout(layout)
    
    def refresh_file_list(self):
        """Làm mới danh sách file"""
        try:
            result, status_code = self.api_service.get_user_files()
            
            if status_code == 200 and result.get('error') == 0:
                files = result.get('data', [])
                self.file_list.clear()
                
                for file_info in files:
                    filename = file_info.get('filename', 'Unknown')
                    file_path = file_info.get('filePath', '')
                    item_text = f"{filename} ({file_path})"
                    self.file_list.addItem(item_text)
                
                show_message(self, "Thành công", f"Đã tải {len(files)} file!")
            else:
                error_msg = result.get('message', 'Không thể tải danh sách file')
                show_message(self, "Lỗi", error_msg, "error")
                
        except Exception as e:
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")