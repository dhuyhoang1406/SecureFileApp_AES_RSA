# 🔐 SecureFileApp AES + RSA

Ứng dụng desktop kết hợp một backend Node.js (Express + Sequelize + MySQL) và frontend PyQt (Python). Mục tiêu là mã hóa file bằng AES và bảo vệ/luu trữ metadata liên quan bằng backend. README này mô tả cách chạy project (backend + database + frontend) và mô tả luồng hoạt động hiện tại trong mã nguồn.

## Mục lục

- Yêu cầu trước khi chạy
- Chạy backend (Node.js)
- Chạy migrations / database
- Chạy frontend (PyQt)
- Luồng hoạt động hiện tại (implementation notes)
- Ghi chú bảo mật & cải tiến đề xuất

---

## Yêu cầu trước khi chạy

- Node.js (v16+) và npm
- MySQL server (hoặc MariaDB) đang chạy
- Python 3.8+ (khuyến nghị 3.10/3.11) và pip
- Trên Windows: PowerShell (README này dùng lệnh PowerShell cho ví dụ)

## Cấu trúc chính liên quan

- `backend/` - server Node.js (Express). Sử dụng Sequelize + mysql2.
- `frontend/pyqt/` - ứng dụng desktop PyQt5.
- `crypto/` - module Python xử lý AES/RSA (được frontend import trực tiếp).

---

## 1) Cấu hình & chạy backend

1. Mở terminal, vào thư mục backend:

```powershell
cd backend
```

2. Cài dependency:

```powershell
npm install
```

3. Tạo file `.env` trong `backend/` với các biến môi trường tối thiểu (ví dụ):

```
DATABASE_NAME=securefile_db
DATABASE_USER=root
DATABASE_PASSWORD=your_mysql_password
DATABASE_HOST=127.0.0.1
DATABASE_PORT=3306
PORT=5000
NODE_ENV=development
```

Lưu ý: nếu bạn chưa tạo database, thực hiện bước tạo DB (bên dưới).

4. Tạo database (nếu chưa có). Ví dụ dùng MySQL CLI:

```powershell
# Đăng nhập MySQL và tạo DB (Windows PowerShell)
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS securefile_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

5. Chạy migration (tạo bảng) — project dùng `sequelize-cli`:

```powershell
# Từ thư mục backend
npm run db:migrate
```

Nếu gặp lỗi liên quan đến ESM/CommonJS với `sequelize-cli`, một cách tạm thời là chạy migration bằng cách import module migration trong một script Node nhỏ hoặc cài thêm cấu hình tương thích; trong hầu hết môi trường `npm run db:migrate` sẽ hoạt động (vì project đã có `config/config.js`).

6. Start server:

```powershell
# chế độ phát triển (hot reload)
npm run dev
# hoặc production
npm start
```

Server mặc định lắng nghe trên `PORT` (mặc định 5000). API base URL (frontend mặc định): `http://localhost:5000/api`.

### Các tệp quan trọng (backend)

- `backend/server.js` — cấu hình Express, kết nối DB và mount routes.
- `backend/config/connectDB.js` & `backend/config/config.js` — cấu hình Sequelize từ `.env`.
- `backend/migrations/` — migrations tạo bảng `Users` và `Files`.
- `backend/keys/jwt_private.pem`, `backend/keys/jwt_public.pem` — key dùng để sign JWT (server currently reads private key from `keys/jwt_private.pem`).

---

## 2) Chạy frontend (PyQt)

1. Tạo và kích hoạt virtual environment (Windows PowerShell):

```powershell
cd frontend/pyqt
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Cài packages:

```powershell
pip install -r requirements.txt
```

3. Cấu hình API (nếu cần) — mặc định `frontend/pyqt/utils/config.py` chứa:

```python
API_BASE_URL = "http://localhost:5000/api"
DEMO_MODE = False
```

Đặt `DEMO_MODE = True` nếu bạn muốn chạy UI mà không cần backend (nhiều API trả về mock responses khi bật demo mode).

4. Chạy ứng dụng:

```powershell
python main.py
```

Ứng dụng sẽ mở cửa sổ chính (login, list files, upload encrypt, decrypt-hàm placeholder).

---

## 3) Luồng hoạt động hiện tại (theo mã nguồn)

Ghi chú: phần này mô tả luồng thực tế như được cài trong code tại thời điểm này (không phải luồng ý tưởng ban đầu). Tôi tóm tắt các bước chính:

1. Đăng ký / Đăng nhập

   - Frontend gọi `POST /api/auth/register` (email, password, repeatPassword).
   - Đăng nhập `POST /api/auth/login` trả về: `{ token, userId }` (token là JWT do server sign bằng file `keys/jwt_private.pem`).

2. Xác thực API

   - Middleware `JWTAction` đọc token từ header `Authorization: Bearer <token>` và header `x-user-id`.
   - Middleware kiểm tra token có nằm trong blacklist (logout) và xác minh token bằng public key lấy từ DB (user record) thông qua `get_publicKey_Token`.
   - Nếu hợp lệ, `req.data` sẽ chứa payload token (ví dụ `id`) và request được tiếp tục.

3. Upload (mã hóa) file

   - Frontend có hàm `CryptoUtils.generate_aes_key()` tạo AES key (base64), dùng `CryptoUtils.encrypt_file()` để mã hóa file locally.
   - Sau khi có file `.enc`, frontend gửi metadata tới backend: `POST /api/file/upload` với JSON `{ filename, filePath, aesKey }`.
   - Backend lưu `filePath`, `filename`, và `aesKey` vào bảng `Files` (hàm `file-service.uploadFile`).

4. Lấy danh sách file

   - Frontend gọi `GET /api/file/list` (middleware xác thực) để nhận danh sách file user.

5. Giải mã (hiện tại chưa hoàn chỉnh hoàn toàn)
   - Frontend có hàm `download_and_decrypt_file` và `CryptoUtils.decrypt_file` sử dụng `crypto/aes_decrypt.py` để giải mã file cục bộ khi có AES key.
   - Tuy nhiên API download file chưa rõ/cụ thể — hiện implementation có chỗ là placeholder.

---

## 4) Các lưu ý quan trọng & cải tiến đề xuất

- Hiện tại AES key được frontend gửi và backend lưu thẳng trong trường `aesKey` của bảng `Files` (base64). Điều này KHÔNG an toàn nếu lưu plain-key trong DB.

  - Đề xuất: frontend nên wrap (mã hóa) AES key bằng RSA public key của user trước khi gửi. Backend lưu AES key đã được wrap (ciphertext). Khi cần giải mã, user dùng RSA private key (lưu cẩn thận) để unwrap.
  - Trong repo có thư mục `crypto/cryptoRSA_test/rsa_wrap_key.py` và helper `CryptoUtils.wrap_aes_key_with_rsa`/`unwrap_aes_key_with_rsa` để hỗ trợ chức năng này — bạn có thể tích hợp chúng vào luồng upload/download.

- JWT signing / verification: hiện server sign JWT bằng `keys/jwt_private.pem` (server-side), nhưng middleware `JWTAction` dùng publicKey lấy từ user record trong DB để verify — đây có thể là sai lệch logic (server-signed token lẽ ra được verify bằng public key tương ứng với private key đã sign). Kiểm tra lại cơ chế dùng key để sign/verify.

- Migrations: project dùng `sequelize-cli`. Nếu `npm run db:migrate` gặp lỗi do module ESM, bạn có thể tạm chạy migration bằng script Node tùy chỉnh hoặc chuyển cấu hình `sequelize-cli` để dùng CommonJS.

---

## 5) Ví dụ chạy nhanh (Windows PowerShell)

```powershell
# 1) Backend
cd d:\Code\Code Python\ATBM_DoAn\SecureFileApp_AES_RSA\backend
npm install
# tạo database trước nếu cần
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS securefile_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# tạo .env như ví dụ ở trên
npm run db:migrate
npm run dev

# 2) Frontend (một terminal khác)
cd d:\Code\Code Python\ATBM_DoAn\SecureFileApp_AES_RSA\frontend\pyqt
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

---

Nếu bạn muốn, tôi có thể tiếp tục và:

- Thêm script seed data (tạo user mẫu) hoặc endpoint download file mẫu.
- Tích hợp wrapping AES key bằng RSA trong đường dẫn upload/download (an toàn hơn).
- Sửa README để thêm troubleshooting khi `sequelize-cli` báo lỗi ESM.

Cho tôi biết bạn muốn tôi bổ sung phần nào tiếp theo hoặc tôi có thể tạo file `.env.example` và script seed để bạn chạy nhanh.

---
