import requests
import json
from PyQt5.QtCore import QThread, pyqtSignal
from utils.config import API_BASE_URL, DEMO_MODE

class APIService:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None
        self.user_id = None
        self.demo_mode = DEMO_MODE
    
    def set_token(self, token):
        """Thiết lập JWT token cho authentication"""
        self.token = token
    
    def set_user_id(self, user_id):
        """Thiết lập User ID cho các API yêu cầu header x-user-id"""
        self.user_id = user_id
    
    def get_headers(self):
        """Tạo headers cho API request"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        if self.user_id:
            headers['x-user-id'] = str(self.user_id)
        return headers
    
    def register(self, email, password):
        """Đăng ký tài khoản mới"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time
            time.sleep(0.5)  # Simulate network delay
            return {
                'error': 0,
                'message': 'Đăng ký thành công (DEMO MODE)'
            }, 201
        
        try:
            data = {
                'email': email,
                'password': password,
                'repeatPassword': password  # Backend yêu cầu repeatPassword
            }
            response = requests.post(
                f'{self.base_url}/auth/register',
                json=data,
                headers=self.get_headers()
            )
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def login(self, email, password):
        """Đăng nhập"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time
            time.sleep(0.5)  # Simulate network delay
            mock_token = "demo_token_12345"
            mock_user_id = "demo_user_001"
            self.set_token(mock_token)
            self.set_user_id(mock_user_id)
            return {
                'error': 0,
                'message': 'Đăng nhập thành công (DEMO MODE)',
                'token': mock_token,
                'userId': mock_user_id
            }, 200
        
        try:
            data = {
                'email': email,
                'password': password
            }
            response = requests.post(
                f'{self.base_url}/auth/login',
                json=data,
                headers=self.get_headers()
            )
            result = response.json()
            if response.status_code == 200 and 'token' in result:
                self.set_token(result['token'])
                if 'userId' in result:
                    self.set_user_id(result['userId'])
            return result, response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def encrypt_file(self, file_path):
        """Mã hóa file - theo API hiện tại: gửi metadata JSON (filename, filePath, aesKey)"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time, os
            time.sleep(1.0)  # Simulate encryption time
            filename = os.path.basename(file_path)
            return {
                'error': 0,
                'message': f'File {filename} đã được mã hóa (DEMO MODE)',
                'encrypted_file_path': f'/demo/encrypted/{filename}.enc'
            }, 200
        
        try:
            import os, base64, secrets
            filename = os.path.basename(file_path)
            # Tạo AES key ngẫu nhiên 256-bit (base64)
            aes_key = base64.b64encode(secrets.token_bytes(32)).decode()
            payload = {
                'filename': filename,
                'filePath': file_path,
                'aesKey': aes_key
            }
            response = requests.post(
                f'{self.base_url}/file/upload',
                json=payload,
                headers=self.get_headers()
            )
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def decrypt_file(self, file_path):
        """Giải mã file - Download và giải mã file"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time, os
            time.sleep(1.0)  # Simulate decryption time
            filename = os.path.basename(file_path)
            return {
                'error': 0,
                'message': f'File {filename} đã được giải mã (DEMO MODE)',
                'decrypted_file_path': f'/demo/decrypted/{filename}'
            }, 200
        
        try:
            # Tạm thời return placeholder - cần implement download API
            return {'message': 'Decrypt API chưa sẵn sàng'}, 501
        except Exception as e:
            return {'error': str(e)}, 500
    
    def get_user_files(self):
        """Lấy danh sách file của user"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time
            time.sleep(0.3)
            return {
                'error': 0,
                'message': 'Success (DEMO MODE)',
                'data': [
                    {'filename': 'document1.pdf', 'filePath': '/demo/encrypted/document1.pdf.enc'},
                    {'filename': 'image.jpg', 'filePath': '/demo/encrypted/image.jpg.enc'},
                    {'filename': 'data.txt', 'filePath': '/demo/encrypted/data.txt.enc'}
                ]
            }, 200
        
        try:
            response = requests.get(
                f'{self.base_url}/file/list',
                headers=self.get_headers()
            )
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def save_user_keys(self, public_key, private_key):
        """Lưu RSA keys của user"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time
            time.sleep(0.3)
            return {
                'error': 0,
                'message': 'Keys đã được lưu (DEMO MODE)'
            }, 200
        
        try:
            data = {
                'publicKey': public_key,
                'privateKey': private_key
            }
            response = requests.post(
                f'{self.base_url}/user/save-key',
                json=data,
                headers=self.get_headers()
            )
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def get_user_keys(self):
        """Lấy RSA keys của user"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time, base64, secrets
            time.sleep(0.3)
            return {
                'error': 0,
                'message': 'Success (DEMO MODE)',
                'data': {
                    'publicKey': base64.b64encode(secrets.token_bytes(256)).decode(),
                    'privateKey': base64.b64encode(secrets.token_bytes(512)).decode()
                }
            }, 200
        
        try:
            response = requests.get(
                f'{self.base_url}/user/get-key',
                headers=self.get_headers()
            )
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500

class APIWorker(QThread):
    """Worker thread để xử lý API calls không block UI"""
    finished = pyqtSignal(dict, int)
    progress = pyqtSignal(int)
    
    def __init__(self, api_service, method, *args, **kwargs):
        super().__init__()
        self.api_service = api_service
        self.method = method
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Chạy API call trong background thread"""
        try:
            method_func = getattr(self.api_service, self.method)
            result, status_code = method_func(*self.args, **self.kwargs)
            self.finished.emit(result, status_code)
        except Exception as e:
            self.finished.emit({'error': str(e)}, 500)