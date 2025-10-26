
import os
import shutil
import base64
import secrets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QFileInfo

# Import trực tiếp từ crypto/ (không dùng subprocess)
from crypto.aes_encrypt import encrypt_file_data
from crypto.aes_decrypt import decrypt_file_data
from crypto.cryptoRSA_test.rsa_wrap_key import seal_aes_key, open_aes_key


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
    import hashlib
    hash_obj = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
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


class CryptoUtils:
    @staticmethod
    def generate_aes_key() -> str:
        """Tạo AES key 16 bytes, trả về base64"""
        return base64.b64encode(secrets.token_bytes(16)).decode()

    @staticmethod
    def encrypt_file(input_file: str, output_file: str, aes_key_b64: str):
        """Mã hóa file bằng AES (gọi trực tiếp hàm từ aes_encrypt.py)"""
        with open(input_file, 'rb') as f:
            data = f.read()
        encrypted_data = encrypt_file_data(data, aes_key_b64)
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)

    @staticmethod
    def decrypt_file(input_file: str, output_file: str, aes_key_b64: str):
        """Giải mã file bằng AES (gọi trực tiếp hàm từ aes_decrypt.py)"""
        with open(input_file, 'rb') as f:
            data = f.read()
        decrypted_data = decrypt_file_data(data, aes_key_b64)
        with open(output_file, 'wb') as f:
            f.write(decrypted_data)

    @staticmethod
    def wrap_aes_key_with_rsa(aes_key_b64: str, public_key_str: str) -> str:
        """
        Mã hóa AES key bằng RSA public key (string 'n,e')
        Trả về encrypted key (base64)
        """
        key_bytes = base64.b64decode(aes_key_b64)
        encrypted_bytes = seal_aes_key(key_bytes, public_key_str)
        return base64.b64encode(encrypted_bytes).decode()

    @staticmethod
    def unwrap_aes_key_with_rsa(encrypted_key_b64: str, private_key_str: str) -> str:
        """
        Giải mã encrypted AES key bằng RSA private key (string 'n,d')
        Trả về AES key (base64)
        """
        enc_bytes = base64.b64decode(encrypted_key_b64)
        key_bytes = open_aes_key(enc_bytes, private_key_str)
        return base64.b64encode(key_bytes).decode()