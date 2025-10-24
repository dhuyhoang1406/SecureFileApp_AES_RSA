# SecureFile App - Frontend PyQt

Ứng dụng desktop để tương tác với hệ thống mã hóa file AES + RSA.

## 🔧 Cài đặt

1. Cài đặt Python dependencies:
```bash
pip install -r requirements.txt
```

2. Chạy ứng dụng:
```bash
python main.py
```

## 📁 Cấu trúc thư mục

```
pyqt/
├── 📄 main.py                 # Entry point của ứng dụng
├── 📄 requirements.txt        # Python dependencies  
├── 📄 README.md              # Hướng dẫn sử dụng
├── 📄 test_backend.py        # Script test backend API
├── 📁 ui/                    # Giao diện người dùng
│   ├── main_window.py        # Cửa sổ chính với tab
│   ├── login_widget.py       # Widget đăng nhập/đăng ký
│   ├── file_operation_widget.py # Widget mã hóa/giải mã file
│   └── advanced_widgets.py  # Key management & file list
├── 📁 services/              # Dịch vụ kết nối API
│   └── api_service.py        # Service giao tiếp backend
├── 📁 utils/                 # Tiện ích hỗ trợ
│   ├── config.py            # Cấu hình ứng dụng
│   └── helpers.py           # Hàm hỗ trợ
└── 📁 assets/               # Tài nguyên (icons, images)
```

## 🚀 Tính năng

### 1. **Đăng nhập/Đăng ký**
- Đăng ký tài khoản mới với email và mật khẩu
- Đăng nhập và nhận JWT token
- Xác thực với backend API (`/auth/register`, `/auth/login`)

### 2. **Tab "Mã hóa File"**
- Chọn file từ máy tính
- Upload file để mã hóa bằng API `/file/upload`
- Hiển thị thông tin file (tên, kích thước, loại)
- Progress bar và log chi tiết

### 3. **Tab "Danh sách File"**
- Hiển thị danh sách file đã mã hóa
- Làm mới danh sách qua API `/file/list`
- Quản lý files đã upload

### 4. **Tab "Quản lý Keys"**
- Hiển thị RSA public/private keys
- Tạo keys mới (tích hợp với crypto modules)
- Lưu/tải keys qua API `/user/save-key`, `/user/get-key`

### 5. **Giao diện**
- Tab-based interface thân thiện
- Responsive design với PyQt5
- Thông báo lỗi/thành công rõ ràng
- Menu và status bar

## 🔗 API Integration

Ứng dụng đã được cập nhật để tương thích với backend thực tế:

### Authentication APIs:
- `POST /api/auth/register` - Đăng ký (email, password, repeatPassword)
- `POST /api/auth/login` - Đăng nhập (trả về JWT token)

### File APIs (cần JWT):
- `POST /api/file/upload` - Upload và mã hóa file
- `GET /api/file/list` - Lấy danh sách file đã mã hóa

### User APIs (cần JWT):
- `POST /api/user/save-key` - Lưu RSA keys
- `GET /api/user/get-key` - Lấy RSA keys
- `PUT /api/user/change-password` - Đổi mật khẩu

## 🧪 Testing

- Nếu nhóm Backend đã cung cấp URL máy chủ, cập nhật biến `API_BASE_URL` trong `utils/config.py` cho phù hợp và chạy:
```bash
python main.py
```
- Tùy chọn: Bạn có thể dùng `test_backend.py` để gọi nhanh các API (khi có URL backend hợp lệ):
```bash
python test_backend.py
```

## ⚙️ Cấu hình

- **Backend URL**: Cập nhật `API_BASE_URL` trong `utils/config.py` tới máy chủ của nhóm Backend (ví dụ: `https://api.yourteam.com/api`).
- **JWT Authentication**: Tự động xử lý trong `api_service.py` (gửi `Authorization` và `x-user-id`).
- **UI Styling**: Tùy chỉnh trong `utils/config.py`.

## 📋 Checklist tích hợp

### ✅ Đã hoàn thành:
- [x] Cấu trúc frontend PyQt hoàn chỉnh
- [x] API integration với backend thực tế
- [x] UI với 3 tabs: File Operation, File List, Key Management
- [x] JWT token management
- [x] Error handling và user feedback
- [x] Test script cho backend APIs

### 🔄 Cần tích hợp với team:
- [ ] **Người 1 (AES)**: Tích hợp AES encrypt/decrypt functions
- [ ] **Người 2 (RSA)**: Tích hợp RSA key generation và hybrid encryption
- [ ] **Người 3-4 (Backend)**: Hoàn thiện file upload/download APIs
- [ ] **Database**: Đảm bảo tables users & files đã được migrate

## 🔧 Hướng dẫn tích hợp

### Cho người làm Crypto (1 & 2):
1. Đặt crypto modules trong folder `crypto/`
2. Import vào `services/api_service.py` hoặc `utils/helpers.py`
3. Cập nhật `generate_new_keys()` trong `advanced_widgets.py`

### Cho người làm Backend (3 & 4):
1. Đảm bảo backend chạy ở port 5000
2. Implement multer cho file upload
3. Thêm file download API cho decrypt
4. Test với `python test_backend.py`

## 🎯 Next Steps

1. Nhận URL backend từ nhóm Backend và cập nhật `API_BASE_URL`.
2. Test APIs (tùy chọn): `python test_backend.py` với URL hợp lệ.
3. Chạy frontend: `python main.py`.
4. Tích hợp crypto modules khi nhóm Crypto hoàn thành.

Frontend đã sẵn sàng để tích hợp với toàn bộ hệ thống! 🚀