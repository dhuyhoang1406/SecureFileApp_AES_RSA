# 🔐 SecureFileApp AES + RSA

Ứng dụng mã hóa tập tin sử dụng **AES** (mã hóa đối xứng) và **RSA** (mã hóa bất đối xứng).  
Mục tiêu: Bảo vệ dữ liệu người dùng bằng cách mã hóa file với AES và bảo mật khóa AES bằng RSA.  

---

## 📌 Cách hoạt động

1. **Đăng ký / Đăng nhập**
   - Người dùng tạo tài khoản, đăng nhập vào hệ thống.
   - Hệ thống quản lý thông tin và khóa của người dùng trong cơ sở dữ liệu.

2. **Mã hóa file**
   - Người dùng chọn file cần mã hóa trên giao diện.
   - Ứng dụng sinh khóa AES ngẫu nhiên → dùng để mã hóa dữ liệu.
   - Khóa AES được mã hóa lại bằng RSA (khóa công khai của người dùng).
   - Trả về file đã mã hóa cho người dùng lưu trữ.

3. **Giải mã file**
   - Người dùng tải file đã mã hóa lên ứng dụng.
   - Hệ thống dùng khóa riêng RSA để giải mã khóa AES.
   - Khóa AES sau đó được dùng để giải mã nội dung file.
   - Trả về file gốc cho người dùng.

---

## ⚡ Thành phần chính
- **Backend**: Spring Boot + MySQL (quản lý user, khóa, API encrypt/decrypt).  
- **Frontend**: Python Tkinter / PyQt (giao diện desktop: login, upload, encrypt, decrypt).  
- **Crypto Core**: AES (128/192/256 bit), RSA (2048 bit) kết hợp thành Hybrid.  

---

## 🧪 Chức năng
- Đăng ký / Đăng nhập  
- Mã hóa file bằng AES  
- Bảo mật khóa AES bằng RSA  
- Giải mã file  
- Giao diện desktop đơn giản, dễ sử dụng  

---
