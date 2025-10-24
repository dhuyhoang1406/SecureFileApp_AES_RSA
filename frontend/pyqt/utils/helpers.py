import os
import hashlib
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QFileInfo

def show_message(parent, title, message, msg_type="info"):
    """Hiển thị message box"""
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(message)
    
    if msg_type == "error":
        msg.setIcon(QMessageBox.Critical)
    elif msg_type == "warning":
        msg.setIcon(QMessageBox.Warning)
    elif msg_type == "question":
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    else:
        msg.setIcon(QMessageBox.Information)
    
    return msg.exec_()

def validate_file(file_path, max_size=None):
    """Kiểm tra file hợp lệ"""
    if not os.path.exists(file_path):
        return False, "File không tồn tại"
    
    if not os.path.isfile(file_path):
        return False, "Đây không phải là file"
    
    if max_size and os.path.getsize(file_path) > max_size:
        return False, f"File quá lớn (tối đa {max_size // (1024*1024)}MB)"
    
    return True, "File hợp lệ"

def get_file_info(file_path):
    """Lấy thông tin file"""
    if not os.path.exists(file_path):
        return None
    
    file_info = QFileInfo(file_path)
    return {
        'name': file_info.fileName(),
        'size': file_info.size(),
        'extension': file_info.suffix(),
        'path': file_path,
        'directory': file_info.dir().path()
    }

def calculate_file_hash(file_path, algorithm='sha256'):
    """Tính hash của file"""
    hash_obj = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        return None

def format_file_size(size_bytes):
    """Format kích thước file"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def sanitize_filename(filename):
    """Làm sạch tên file"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename