from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QGroupBox,
                             QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
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
        priv_label = QLabel("Private Key:")
        self.private_key_text = QTextEdit()
        self.private_key_text.setMaximumHeight(100)
        self.private_key_text.setReadOnly(True)
        self.private_key_text.setPlaceholderText("Private key sẽ hiển thị ở đây...")
        
        key_layout.addWidget(pub_label)
        key_layout.addWidget(self.public_key_text)
        key_layout.addWidget(priv_label)
        key_layout.addWidget(self.private_key_text)
        
        key_section.setLayout(key_layout)
        layout.addWidget(key_section)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.load_keys_btn = QPushButton("Tải Keys")
        self.load_keys_btn.setStyleSheet(BUTTON_STYLE)
        self.load_keys_btn.clicked.connect(self.load_user_keys)
        
        self.generate_keys_btn = QPushButton("Tạo Keys mới")
        self.generate_keys_btn.setStyleSheet(BUTTON_STYLE)
        self.generate_keys_btn.clicked.connect(self.generate_new_keys)
        
        button_layout.addWidget(self.load_keys_btn)
        button_layout.addWidget(self.generate_keys_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_user_keys(self):
        """Tải RSA keys từ server"""
        try:
            result, status_code = self.api_service.get_user_keys()
            
            if status_code == 200 and result.get('error') == 0:
                keys = result.get('data', {})
                self.public_key_text.setText(keys.get('publicKey', ''))
                self.private_key_text.setText(keys.get('privateKey', ''))
                show_message(self, "Thành công", "Đã tải keys thành công!")
            else:
                error_msg = result.get('message', 'Không thể tải keys')
                show_message(self, "Lỗi", error_msg, "error")
                
        except Exception as e:
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")
    
    def generate_new_keys(self):
        """Tạo RSA keys mới (placeholder - cần crypto module)"""
        # Tạm thời dùng placeholder keys
        import secrets
        import base64
        
        # Tạo fake keys để demo
        public_key = base64.b64encode(secrets.token_bytes(256)).decode()
        private_key = base64.b64encode(secrets.token_bytes(512)).decode()
        
        self.public_key_text.setText(public_key)
        self.private_key_text.setText(private_key)
        
        # Lưu lên server
        try:
            result, status_code = self.api_service.save_user_keys(public_key, private_key)
            
            if status_code == 200 and result.get('error') == 0:
                show_message(self, "Thành công", "Đã tạo và lưu keys mới!")
            else:
                error_msg = result.get('message', 'Không thể lưu keys')
                show_message(self, "Lỗi", error_msg, "error")
                
        except Exception as e:
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")

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