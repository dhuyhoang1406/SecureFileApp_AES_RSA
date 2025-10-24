from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QStackedWidget, QMenuBar, QStatusBar, QAction,
                             QTabWidget, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from services.api_service import APIService
from ui.login_widget import LoginWidget
from ui.file_operation_widget import FileOperationWidget
from ui.advanced_widgets import KeyManagementWidget, FileListWidget
from utils.config import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
from utils.helpers import show_message

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_service = APIService()
        self.current_user_token = None
        self.init_ui()
        self.setup_menu()
        self.setup_status_bar()
    
    def init_ui(self):
        """Khởi tạo giao diện chính"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Central widget với stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Stacked widget để chuyển đổi giữa các màn hình
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Tạo các widget
        self.login_widget = LoginWidget(self.api_service)
        
        # Tạo tab widget cho main application
        self.main_tab_widget = QTabWidget()
        self.file_operation_widget = FileOperationWidget(self.api_service)
        self.key_management_widget = KeyManagementWidget(self.api_service)
        self.file_list_widget = FileListWidget(self.api_service)
        
        # Thêm tabs
        self.main_tab_widget.addTab(self.file_operation_widget, "📁 Mã hóa File")
        self.main_tab_widget.addTab(self.file_list_widget, "📋 Danh sách File")
        self.main_tab_widget.addTab(self.key_management_widget, "🔑 Quản lý Keys")
        
        # Thêm vào stack
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.main_tab_widget)
        
        # Bắt đầu với màn hình login
        self.stacked_widget.setCurrentWidget(self.login_widget)
        
        # Kết nối signals
        self.login_widget.login_success.connect(self.on_login_success)
    
    def setup_menu(self):
        """Thiết lập menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Logout action
        self.logout_action = QAction('Đăng xuất', self)
        self.logout_action.triggered.connect(self.logout)
        self.logout_action.setEnabled(False)
        file_menu.addAction(self.logout_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Thoát', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Trợ giúp')
        
        about_action = QAction('Về ứng dụng', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Thiết lập status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Chưa đăng nhập")
    
    def on_login_success(self, token):
        """Xử lý khi đăng nhập thành công"""
        self.current_user_token = token
        self.api_service.set_token(token)
        
        # Chuyển sang màn hình chính
        self.stacked_widget.setCurrentWidget(self.main_tab_widget)
        
        # Cập nhật UI
        self.logout_action.setEnabled(True)
        self.status_bar.showMessage("Đã đăng nhập - Sẵn sàng sử dụng")
        
        # Thêm log
        self.file_operation_widget.add_log("Đăng nhập thành công!")
    
    def logout(self):
        """Đăng xuất"""
        reply = show_message(
            self, 
            "Xác nhận", 
            "Bạn có chắc chắn muốn đăng xuất?", 
            "question"
        )
        
        if reply == QMessageBox.Yes:
            # Reset token
            self.current_user_token = None
            self.api_service.set_token(None)
            
            # Quay về màn hình login
            self.stacked_widget.setCurrentWidget(self.login_widget)
            
            # Reset form đăng nhập
            self.login_widget.email_input.clear()
            self.login_widget.password_input.clear()
            
            # Reset file operation
            self.file_operation_widget.clear_file()
            self.file_operation_widget.clear_log()
            self.file_operation_widget.add_log("Đã đăng xuất")
            
            # Clear other widgets
            self.key_management_widget.public_key_text.clear()
            self.key_management_widget.private_key_text.clear()
            self.file_list_widget.file_list.clear()
            
            # Cập nhật UI
            self.logout_action.setEnabled(False)
            self.status_bar.showMessage("Chưa đăng nhập")
    
    def show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        about_text = """
        <h3>SecureFile App - AES + RSA Encryption</h3>
        <p><b>Phiên bản:</b> 1.0.0</p>
        <p><b>Mô tả:</b> Ứng dụng mã hóa/giải mã file sử dụng thuật toán AES và RSA</p>
        <p><b>Tính năng:</b></p>
        <ul>
            <li>Đăng ký/Đăng nhập người dùng</li>
            <li>Mã hóa file bằng AES + RSA (Hybrid)</li>
            <li>Giải mã file an toàn</li>
            <li>Giao diện thân thiện</li>
        </ul>
        <p><b>Phát triển bởi:</b> Nhóm SecureFile Team</p>
        """
        show_message(self, "Về ứng dụng", about_text, "info")
    
    def closeEvent(self, event):
        """Xử lý khi đóng ứng dụng"""
        reply = show_message(
            self,
            "Xác nhận thoát",
            "Bạn có chắc chắn muốn thoát ứng dụng?",
            "question"
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()