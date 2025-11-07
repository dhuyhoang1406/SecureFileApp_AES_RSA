import requests
import json
from PyQt5.QtCore import QThread, pyqtSignal
from utils.config import API_BASE_URL, DEMO_MODE
from utils.helpers import CryptoUtils
import os

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
            import os
            filename = os.path.basename(file_path)
            # Tạo AES key ngẫu nhiên 128-bit (base64)
            aes_key = CryptoUtils.generate_aes_key()
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
            result = response.json()

            # Normalize backend response: backend returns { error:0, files: [...] }
            if isinstance(result, dict):
                if 'files' in result and 'data' not in result:
                    normalized = {'error': result.get('error', 0), 'data': result.get('files', [])}
                    return normalized, response.status_code
                # already in expected shape
                return result, response.status_code

            return result, response.status_code
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
            # backend returns { error:0, message:.. } — return as-is
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def get_user_keys(self):
        """Lấy RSA keys của user - CHỈ TRẢ PUBLIC KEY"""
        if self.demo_mode:
            # Mock response cho demo mode
            import time, base64, secrets
            time.sleep(0.3)
            return {
                'error': 0,
                'message': 'Success (DEMO MODE)',
                'data': {
                    'publicKey': base64.b64encode(secrets.token_bytes(256)).decode(),
                }
            }, 200
        
        try:
            response = requests.get(
                f'{self.base_url}/user/get-key',
                headers=self.get_headers()
            )
            result = response.json()
            # backend returns { error:0, data: { publicKey } }
            return result, response.status_code
        except Exception as e:
            return {'error': str(e)}, 500

    def get_private_key(self, password):
        """Lấy private key - YÊU CẦU XÁC NHẬN PASSWORD"""
        if self.demo_mode:
            import time, base64, secrets
            time.sleep(0.3)
            return {
                'error': 0,
                'message': 'Success (DEMO MODE)',
                'data': {
                    'privateKey': base64.b64encode(secrets.token_bytes(512)).decode()
                }
            }, 200
        
        try:
            response = requests.post(
                f'{self.base_url}/user/get-private-key',
                json={'password': password},
                headers=self.get_headers()
            )
            result = response.json()
            return result, response.status_code
        except Exception as e:
            return {'error': str(e)}, 500

    def logout(self):
        """Logout: gọi backend để invalidate token (blacklist)"""
        if self.demo_mode:
            # In demo mode just clear local token
            self.set_token(None)
            self.set_user_id(None)
            return {'error': 0, 'message': 'Logout (DEMO MODE)'}, 200

        try:
            response = requests.post(
                f'{self.base_url}/auth/logout',
                headers=self.get_headers()
            )
            # Clear local token if backend accepted
            if response.status_code == 200:
                self.set_token(None)
                self.set_user_id(None)
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def share_file(self, file_id, recipient_email):
        """Share file với user khác"""
        if self.demo_mode:
            import time
            time.sleep(0.5)
            return {
                'error': 0,
                'message': f'File đã được share với {recipient_email} (DEMO MODE)'
            }, 200
        
        try:
            response = requests.post(
                f'{self.base_url}/file/share',
                json={'fileId': file_id, 'recipientEmail': recipient_email},
                headers=self.get_headers()
            )
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def download_file_key(self, file_id, save_path):
        """
        Tải file .enc.key về máy (binary download)
        
        Args:
            file_id: ID của file trên server
            save_path: Đường dẫn đầy đủ nơi lưu file .enc.key
            
        Returns:
            tuple: (dict/None, status_code)
                   Success: (None, 200) - file đã lưu vào save_path
                   Error: ({'error': msg}, status_code)
        """
        if self.demo_mode:
            import time, secrets
            time.sleep(0.5)
            # Mock: tạo fake key file (64 bytes wrapped key)
            with open(save_path, 'wb') as f:
                f.write(secrets.token_bytes(64))
            return None, 200
        
        try:
            response = requests.get(
                f'{self.base_url}/file/{file_id}/download-key',
                headers=self.get_headers(),
                stream=True  # Stream để tải file binary
            )
            
            if response.status_code == 200:
                # Lưu file binary
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return None, 200
            else:
                # Lỗi - response có thể là JSON
                try:
                    error_data = response.json()
                    return error_data, response.status_code
                except:
                    return {'error': f'HTTP {response.status_code}'}, response.status_code
                    
        except Exception as e:
            return {'error': str(e)}, 500
    
    def download_file(self, file_id):
        """Tải nội dung file đã mã hóa từ server"""
        if self.demo_mode:
            import time, base64
            time.sleep(0.5)
            # Fake encrypted content
            fake_content = b'This is demo encrypted file content'
            return {
                'error': 0,
                'data': {
                    'content': base64.b64encode(fake_content).decode(),
                    'filename': 'demo_file.txt.enc'
                }
            }, 200
        
        try:
            response = requests.get(
                f'{self.base_url}/file/{file_id}/download',
                headers=self.get_headers()
            )
            return response.json(), response.status_code
        except Exception as e:
            return {'error': str(e)}, 500
    
    def encrypt_and_upload_file(self, file_path):
        """
        Mã hóa file và upload lên backend.
        """
        try:
            # Mã hóa file
            encrypted_file_path = f"{file_path}.enc"
            aes_key = CryptoUtils.generate_aes_key()
            CryptoUtils.encrypt_file(file_path, encrypted_file_path, aes_key)

            # Upload file đã mã hóa
            filename = os.path.basename(file_path)
            payload = {
                'filename': filename,
                'filePath': encrypted_file_path,
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

    def download_and_decrypt_file(self, file_path, aes_key):
        """
        Tải file từ backend và giải mã.
        """
        try:
            # Tạm thời return placeholder - cần implement download API
            decrypted_file_path = file_path.replace(".enc", ".dec")
            CryptoUtils.decrypt_file(file_path, decrypted_file_path, aes_key)
            return {'message': 'File đã được giải mã', 'decrypted_file_path': decrypted_file_path}, 200
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