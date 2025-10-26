from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from utils.config import BUTTON_STYLE
from utils.helpers import show_message

class LoginWidget(QWidget):
    login_success = pyqtSignal(str)  # Signal khi login thành công, truyền token
    
    def __init__(self, api_service):
        super().__init__()
        self.api_service = api_service
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Title
        title = QLabel("Đăng nhập vào SecureFile App")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Login form
        form_frame = QFrame()
        form_frame.setMaximumWidth(400)
        form_frame.setStyleSheet("QFrame { border: 1px solid #ccc; border-radius: 10px; padding: 20px; }")
        form_layout = QVBoxLayout(form_frame)
        
        # Email input
        email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email của bạn")
        self.email_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        form_layout.addWidget(email_label)
        form_layout.addWidget(self.email_input)
        
        # Password input
        password_label = QLabel("Mật khẩu:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; border: 1px solid #ccc; border-radius: 5px;")
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("Đăng nhập")
        self.login_btn.setStyleSheet(BUTTON_STYLE)
        self.login_btn.clicked.connect(self.handle_login)
        
        self.register_btn = QPushButton("Đăng ký")
        self.register_btn.setStyleSheet(BUTTON_STYLE)
        self.register_btn.clicked.connect(self.handle_register)
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)
        form_layout.addLayout(button_layout)
        
        layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        
        # Enter key shortcuts
        self.email_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
    
    def handle_login(self):
        """Xử lý đăng nhập"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            show_message(self, "Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu", "error")
            return
        
        # Disable buttons
        self.login_btn.setEnabled(False)
        self.register_btn.setEnabled(False)
        self.login_btn.setText("Đang đăng nhập...")
        
        # Call API
        try:
            result, status_code = self.api_service.login(email, password)
            
            if status_code == 200 and 'token' in result:
                show_message(self, "Thành công", "Đăng nhập thành công!")
                self.login_success.emit(result['token'])
            else:
                error_msg = result.get('message', 'Đăng nhập thất bại')
                show_message(self, "Lỗi", error_msg, "error")
        
        except Exception as e:
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")
        
        finally:
            # Re-enable buttons
            self.login_btn.setEnabled(True)
            self.register_btn.setEnabled(True)
            self.login_btn.setText("Đăng nhập")
    
    def handle_register(self):
        """Xử lý đăng ký"""
        email = self.email_input.text().strip()
        password = self.password_input.text()
        
        if not email or not password:
            show_message(self, "Lỗi", "Vui lòng nhập đầy đủ email và mật khẩu", "error")
            return
        
        if len(password) < 6:
            show_message(self, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự", "error")
            return
        
        # Disable buttons
        self.login_btn.setEnabled(False)
        self.register_btn.setEnabled(False)
        self.register_btn.setText("Đang đăng ký...")
        
        # Call API
        try:
            result, status_code = self.api_service.register(email, password)
            
            # Backend may return 200 or 201 — treat both as success when error==0
            if status_code in (200, 201) and result.get('error', 0) == 0:
                show_message(self, "Thành công", "Đăng ký thành công! Vui lòng đăng nhập.")
                self.password_input.clear()
            else:
                error_msg = result.get('message', 'Đăng ký thất bại')
                show_message(self, "Lỗi", error_msg, "error")
        
        except Exception as e:
            show_message(self, "Lỗi", f"Lỗi kết nối: {str(e)}", "error")
        
        finally:
            # Re-enable buttons
            self.login_btn.setEnabled(True)
            self.register_btn.setEnabled(True)
            self.register_btn.setText("Đăng ký")