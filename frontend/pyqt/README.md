# SecureFile App - Ứng dụng Mã hóa File với AES + RSA

Ứng dụng desktop bảo mật cao sử dụng **Hybrid Encryption** (AES-128 + RSA-512) để mã hóa file và chia sẻ an toàn giữa nhiều người dùng.

## 🎯 Tổng quan hệ thống

### Kiến trúc
```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Frontend PyQt  │ ◄─────► │  Backend Node.js │ ◄─────► │  SQLite Database│
│  (Python)       │   HTTP  │  (Express)       │         │  (Users, Files) │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                            │
        │                            │
        ▼                            ▼
┌─────────────────┐         ┌──────────────────┐
│  Crypto Modules │         │  RSA Crypto      │
│  (AES Python)   │         │  (Node.js)       │
└─────────────────┘         └──────────────────┘
```

### Công nghệ sử dụng
- **Frontend**: PyQt5 (Python) - Giao diện desktop
- **Backend**: Node.js + Express + Sequelize
- **Database**: SQLite (Users, Files tables)
- **Mã hóa**: 
  - AES-128 (ECB mode, PKCS#7 padding) cho file
  - RSA-512 cho key wrapping
  - Hybrid Encryption (AES + RSA)

## 🔧 Cài đặt

### 1. Cài đặt Python dependencies:
```bash
cd frontend/pyqt
pip install -r requirements.txt
```

### 2. Cài đặt Backend dependencies:
```bash
cd backend
npm install
```

### 3. Cấu hình Database:
```bash
cd backend
npx sequelize-cli db:migrate
```

### 4. Chạy Backend:
```bash
cd backend
npm run dev
```

### 5. Chạy Frontend:
```bash
cd frontend/pyqt
python main.py
```

## 📁 Cấu trúc dự án đầy đủ

```
SecureFileApp_AES_RSA/
├── � backend/                           # Backend Node.js
│   ├── 📄 server.js                     # Entry point backend
│   ├── 📄 package.json                  # Node.js dependencies
│   ├── 📁 config/
│   │   ├── config.js                   # Cấu hình DB, JWT secret
│   │   └── connectDB.js                # Kết nối SQLite
│   ├── � controller/
│   │   ├── auth-controller.js          # Xử lý đăng nhập/đăng ký
│   │   ├── file-controller.js          # Xử lý upload/share/download file
│   │   └── user-controller.js          # Quản lý user keys
│   ├── 📁 service/
│   │   ├── auth-service.js             # Logic nghiệp vụ auth
│   │   ├── file-service.js             # Logic nghiệp vụ file
│   │   └── user-service.js             # Logic nghiệp vụ user
│   ├── 📁 models/
│   │   ├── index.js                    # Sequelize initialization
│   │   ├── user.js                     # Model User (id, email, password, publicKey, privateKey)
│   │   └── file.js                     # Model File (id, filename, filePath, aesKey, userId)
│   ├── � middleware/
│   │   └── JWTAction.js                # Middleware xác thực JWT token
│   ├── 📁 utils/
│   │   ├── crypto-helper.js            # RSA encrypt/decrypt functions
│   │   └── create-token.js             # Tạo JWT token
│   └── 📁 keys/
│       ├── jwt_private.pem             # Private key để ký JWT
│       └── jwt_public.pem              # Public key để verify JWT
│
├── 📁 frontend/pyqt/                     # Frontend PyQt
│   ├── � main.py                       # Entry point frontend
│   ├── 📄 requirements.txt              # Python dependencies
│   ├── 📁 ui/
│   │   ├── main_window.py              # Cửa sổ chính (tabs)
│   │   ├── login_widget.py             # Màn hình đăng nhập/đăng ký
│   │   ├── file_operation_widget.py    # Tab mã hóa/giải mã/share file
│   │   └── advanced_widgets.py         # Tab quản lý keys & danh sách file
│   ├── 📁 services/
│   │   └── api_service.py              # Service gọi API backend
│   └── 📁 utils/
│       ├── config.py                   # Cấu hình API URL
│       └── helpers.py                  # Wrapper functions cho crypto
│
└── 📁 crypto/                            # Python Crypto Modules
    ├── __init__.py
    ├── aes_encrypt.py                  # AES encryption (ECB, PKCS#7)
    ├── aes_decrypt.py                  # AES decryption
    └── 📁 cryptoRSA_test/
        ├── rsa_wrap_key.py             # RSA key wrapping (seal/open)
        ├── rsa_prv.txt                 # Example RSA private key
        └── rsa_pub.txt                 # Example RSA public key
```

## 🚀 Tính năng chính

### 1. **Đăng ký & Đăng nhập** (`login_widget.py`)
- **Đăng ký tài khoản mới**: Email + Password
  - Backend hash password bằng `bcrypt`
  - Tự động tạo RSA keypair (512-bit) cho user
  - Lưu publicKey, privateKey vào DB
- **Đăng nhập**: Nhận JWT token
  - Token hết hạn sau 24h
  - Auto-refresh khi mở app lại
- **Logout**: Blacklist token trên server

### 2. **Mã hóa File** (`file_operation_widget.py` - `encrypt_file()`)

**Luồng mã hóa (Hybrid Encryption):**
```
1. User chọn file gốc (ví dụ: report.docx)
2. Frontend:
   ├─ Tạo random AES key (16 bytes)
   ├─ Mã hóa file: report.docx --[AES-128]-> report.docx.enc
   ├─ Lấy public key của user từ backend
   ├─ Wrap AES key: AES_key --[RSA-512]-> wrapped_key (64 bytes)
   └─ Gửi metadata lên backend: {filename, filePath, aesKey: wrapped_key}
3. Backend:
   └─ Lưu vào DB: filename, filePath, aesKey (base64 của wrapped_key)
4. Frontend lưu local:
   ├─ report.docx.enc (file đã mã hóa)
   └─ report.docx.enc.key (wrapped key, 64 bytes)
```

**Chi tiết kỹ thuật:**
- **AES-128**: ECB mode, PKCS#7 padding
- **RSA-512**: Textbook RSA (n,e), (n,d)
- **Key format**: "n,e" cho public key, "n,d" cho private key
- **Wrapped key**: Luôn 64 bytes (512-bit RSA)

### 3. **Giải mã File cá nhân** (`file_operation_widget.py` - `decrypt_file()`)

**Luồng giải mã file của chính mình:**
```
1. User chọn file .enc và file .key
2. Nhập password để lấy private key từ backend
3. Frontend:
   ├─ Đọc wrapped key từ file .enc.key (64 bytes)
   ├─ Unwrap: wrapped_key --[RSA với private key]-> AES_key (16 bytes)
   └─ Giải mã: file.enc --[AES-128]-> file gốc
4. Lưu file gốc về máy
```

### 4. **Share File** (`file_operation_widget.py` - `share_file_ui()`)

**Luồng chia sẻ file (Re-wrapping):**
```
1. User A chọn file .enc đã mã hóa
2. Nhập email User B (người nhận)
3. Backend:
   ├─ Lấy wrapped_key_A từ DB (encrypted bằng publicKey_A)
   ├─ Unwrap: wrapped_key_A --[privateKey_A]-> AES_key (plaintext)
   ├─ Re-wrap: AES_key --[publicKey_B]-> wrapped_key_B
   ├─ Tạo file record mới cho User B
   └─ Trả về wrapped_key_B cho frontend
4. Frontend:
   ├─ Nhận wrapped_key_B từ response
   ├─ Ghi vào file: report.docx.enc.key (64 bytes)
   └─ Thông báo: Gửi CẢ HAI FILE (.enc + .enc.key) cho User B
```

**⚠️ Lưu ý quan trọng:**
- File `.enc.key` của User A ≠ File `.enc.key` của User B
- **Cùng 1 file .enc** nhưng **2 wrapped key khác nhau**
- User A giải mã bằng privateKey_A
- User B giải mã bằng privateKey_B
- Cả 2 đều ra **cùng AES key** → giải mã được file gốc

### 5. **Giải mã File được chia sẻ** (`file_operation_widget.py` - `decrypt_shared_file()`)

**Luồng giải mã file từ bạn bè:**
```
1. User B nhận 2 file từ User A:
   ├─ report.docx.enc (file mã hóa)
   └─ report.docx.enc.key (wrapped bằng publicKey_B)
2. User B chọn file .enc (tự động tìm .enc.key cùng thư mục)
3. Nhập password để lấy privateKey_B
4. Frontend:
   ├─ Đọc wrapped_key_B từ file .enc.key
   ├─ Unwrap: wrapped_key_B --[privateKey_B]-> AES_key (16 bytes)
   └─ Giải mã: report.docx.enc --[AES-128]-> report.docx
5. Lưu file gốc về máy
```

### 6. **Quản lý RSA Keys** (`advanced_widgets.py`)

**Tính năng:**
- **Hiển thị Public Key**: Lấy từ backend (`/user/get-key`)
- **Tạo keys mới**: 
  - Generate RSA-512 keypair
  - Lưu lên backend (`/user/save-key`)
- **Lấy Private Key**: Yêu cầu xác nhận password (`/user/get-private-key`)
- **Format key**: "n,e" và "n,d" (BigInt strings)

### 7. **Danh sách File** (`advanced_widgets.py`)

**Hiển thị:**
- Tất cả file đã mã hóa của user
- File được share (prefix `[Shared]`)
- Thông tin: filename, upload time
- Refresh danh sách từ backend (`/file/list`)

## 🔗 API Endpoints

### Authentication APIs (không cần JWT):
```
POST /api/auth/register
Body: { email, password, repeatPassword }
Response: { error: 0, message: "Success" }

POST /api/auth/login  
Body: { email, password }
Response: { error: 0, token: "jwt_token", userId: 123 }

POST /api/auth/logout
Headers: { Authorization: "Bearer <token>" }
Response: { error: 0, message: "Logged out" }
```

### File APIs (cần JWT token):
```
POST /api/file/upload
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Body: { filename, filePath, aesKey }
Response: { error: 0, message: "Success", file: {...} }

GET /api/file/list
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Response: { error: 0, files: [...] }

POST /api/file/share
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Body: { fileId, recipientEmail }
Response: { 
  error: 0, 
  message: "Success",
  sharedFile: {
    id, filename, filePath, 
    aesKey: "base64_wrapped_key_for_recipient",
    userId: recipient_id
  }
}

GET /api/file/:fileId/download-key
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Response: Binary file (wrapped AES key, 64 bytes)

GET /api/file/:fileId/download
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Response: { error: 0, data: { content: "base64_encrypted_file", filename } }
```

### User APIs (cần JWT token):
```
POST /api/user/save-key
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Body: { publicKey: "n,e", privateKey: "n,d" }
Response: { error: 0, message: "Success" }

GET /api/user/get-key
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Response: { error: 0, data: { publicKey: "n,e" } }

POST /api/user/get-private-key
Headers: { Authorization: "Bearer <token>", x-user-id: "123" }
Body: { password }
Response: { error: 0, data: { privateKey: "n,d" } }
```

## 🗄️ Database Schema

### Table: `Users`
```sql
CREATE TABLE Users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,        -- bcrypt hash
  publicKey TEXT,                        -- Format: "n,e"
  privateKey TEXT,                       -- Format: "n,d"
  createdAt DATETIME,
  updatedAt DATETIME
);
```

### Table: `Files`
```sql
CREATE TABLE Files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename VARCHAR(255) NOT NULL,
  filePath TEXT NOT NULL,                -- Đường dẫn file .enc
  aesKey TEXT NOT NULL,                  -- Base64 của wrapped AES key (64 bytes)
  userId INTEGER NOT NULL,
  createdAt DATETIME,
  updatedAt DATETIME,
  FOREIGN KEY (userId) REFERENCES Users(id)
);
```

**Lưu ý:**
- `aesKey` trong DB là **wrapped key** (đã mã hóa bằng RSA), KHÔNG phải plaintext
- Mỗi user có wrapped key riêng cho cùng 1 file (khi share)
- File được share sẽ có prefix `[Shared]` trong filename

## 🔐 Bảo mật

### 1. **Hybrid Encryption**
- **AES-128**: Mã hóa file nhanh, hiệu quả
- **RSA-512**: Bảo vệ AES key, hỗ trợ share file
- **Key Wrapping**: Mỗi user có wrapped key riêng

### 2. **Password Security**
- Hash bằng `bcrypt` (salt rounds = 10)
- Private key yêu cầu password confirmation
- JWT token auto-expire (24h)

### 3. **Token Management**
- JWT signed với RS256 (RSA private key)
- Token blacklist khi logout
- Middleware verify mọi protected routes

### 4. **Data Protection**
- DB chỉ lưu metadata + wrapped keys
- File gốc KHÔNG upload lên server
- Private key KHÔNG trả về khi get public key
- Wrapped key unique cho mỗi user

## 🛠️ Chi tiết kỹ thuật

### Frontend (Python + PyQt5)

**File quan trọng:**

1. **`main.py`**: Entry point, khởi tạo QApplication
2. **`ui/main_window.py`**: MainWindow với TabWidget
3. **`ui/login_widget.py`**: 
   - Xử lý đăng ký/đăng nhập
   - Lưu token vào session
4. **`ui/file_operation_widget.py`**:
   - `encrypt_file()`: Mã hóa file + wrap AES key
   - `decrypt_file()`: Giải mã file cá nhân
   - `share_file_ui()`: Chia sẻ file (re-wrapping)
   - `decrypt_shared_file()`: Giải mã file từ bạn bè
5. **`services/api_service.py`**: 
   - Wrapper cho HTTP requests
   - Auto-attach JWT token và user_id
6. **`utils/helpers.py`**:
   - `CryptoUtils`: Wrapper cho crypto modules
   - `generate_aes_key()`: Random 16 bytes
   - `wrap_aes_key_with_rsa()`: Gọi `seal_aes_key()`
   - `unwrap_aes_key_with_rsa()`: Gọi `open_aes_key()`
   - `encrypt_file()`: Gọi `encrypt_file_data()` từ `crypto/`
   - `decrypt_file()`: Gọi `decrypt_file_data()` từ `crypto/`

### Backend (Node.js + Express)

**File quan trọng:**

1. **`server.js`**: 
   - Express app setup
   - Middleware: cors, body-parser
   - Routes import
2. **`controller/auth-controller.js`**:
   - `register()`: Hash password, tạo RSA keys, lưu DB
   - `login()`: Verify password, tạo JWT token
   - `logout()`: Blacklist token
3. **`controller/file-controller.js`**:
   - `upload()`: Lưu metadata + wrapped key
   - `shareFile()`: **RE-WRAPPING LOGIC**
     ```javascript
     // Unwrap với sender private key
     const aesKey = rsaDecrypt(wrappedKey, senderPrivateKey);
     // Re-wrap với recipient public key
     const newWrappedKey = rsaEncrypt(aesKey, recipientPublicKey);
     ```
   - `downloadKey()`: Trả về wrapped key binary
   - `downloadFile()`: Trả về file .enc content
4. **`utils/crypto-helper.js`**:
   - `generateRSAKeypair()`: Tạo RSA-512 keypair
   - `rsaEncrypt(data, publicKey)`: Textbook RSA encryption
   - `rsaDecrypt(cipher, privateKey)`: Textbook RSA decryption
     - **Padding logic**: Luôn trả về 16 bytes (giống Python)
5. **`middleware/JWTAction.js`**:
   - Verify JWT token
   - Extract user ID
   - Attach `req.data.id`

### Crypto Modules (Python)

**File quan trọng:**

1. **`crypto/aes_encrypt.py`**:
   - `encrypt_file_data(data, aes_key_b64)`: 
     - AES-128 ECB mode
     - PKCS#7 padding
2. **`crypto/aes_decrypt.py`**:
   - `decrypt_file_data(data, aes_key_b64)`:
     - AES-128 ECB mode
     - PKCS#7 unpadding
   - `pkcs7_unpad()`: Verify và remove padding
3. **`crypto/cryptoRSA_test/rsa_wrap_key.py`**:
   - `seal_aes_key(aes_key, public_key)`:
     - Parse "n,e" format
     - RSA encrypt: m^e mod n
     - Return 64 bytes
   - `open_aes_key(wrapped_key, private_key)`:
     - Parse "n,d" format
     - RSA decrypt: c^d mod n
     - **Padding**: `key.rjust(16, b'\x00')` → luôn 16 bytes

## � Luồng hoạt động chi tiết

### Luồng 1: Đăng ký → Đăng nhập → Mã hóa file

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. ĐĂNG KÝ                                                      │
└─────────────────────────────────────────────────────────────────┘
Frontend:
  ├─ User nhập email + password
  └─ POST /api/auth/register { email, password, repeatPassword }

Backend:
  ├─ Hash password (bcrypt)
  ├─ Generate RSA keypair (512-bit)
  │  └─ publicKey: "n,e", privateKey: "n,d"
  ├─ Lưu vào Users table
  └─ Response: { error: 0, message: "Success" }

┌─────────────────────────────────────────────────────────────────┐
│ 2. ĐĂNG NHẬP                                                    │
└─────────────────────────────────────────────────────────────────┘
Frontend:
  ├─ User nhập email + password
  └─ POST /api/auth/login { email, password }

Backend:
  ├─ Verify password (bcrypt compare)
  ├─ Generate JWT token (RS256, expire 24h)
  │  └─ Payload: { id, email }
  └─ Response: { error: 0, token, userId }

Frontend:
  ├─ Lưu token + userId vào session
  └─ Chuyển sang MainWindow

┌─────────────────────────────────────────────────────────────────┐
│ 3. MÃ HÓA FILE                                                  │
└─────────────────────────────────────────────────────────────────┘
Frontend (encrypt_file):
  ├─ 1. User chọn file: report.docx
  ├─ 2. Generate AES key: random 16 bytes → base64
  ├─ 3. Encrypt file:
  │    └─ report.docx --[AES-128 ECB]-> report.docx.enc
  ├─ 4. GET /api/user/get-key → Lấy publicKey
  ├─ 5. Wrap AES key:
  │    └─ seal_aes_key(aes_key_b64, publicKey) → wrapped_key_b64 (64 bytes)
  ├─ 6. POST /api/file/upload
  │    └─ Body: { 
  │         filename: "report.docx", 
  │         filePath: "/temp/report.docx.enc",
  │         aesKey: wrapped_key_b64  ← Wrapped key, KHÔNG phải plaintext
  │       }
  └─ 7. Lưu local:
       ├─ report.docx.enc (encrypted file)
       └─ report.docx.enc.key (wrapped key text file)

Backend (upload):
  ├─ Verify JWT token
  ├─ Lưu vào Files table:
  │  └─ { filename, filePath, aesKey: wrapped_key_b64, userId }
  └─ Response: { error: 0, file: {...} }
```

### Luồng 2: Giải mã file cá nhân

```
┌─────────────────────────────────────────────────────────────────┐
│ 4. GIẢI MÃ FILE CÁ NHÂN                                        │
└─────────────────────────────────────────────────────────────────┘
Frontend (decrypt_file):
  ├─ 1. User chọn file .enc và file .key
  ├─ 2. Nhập password
  ├─ 3. POST /api/user/get-private-key { password }
  │    └─ Backend verify password → Trả privateKey
  ├─ 4. Đọc wrapped_key_b64 từ file .enc.key
  ├─ 5. Unwrap AES key:
  │    └─ open_aes_key(wrapped_key, privateKey) → aes_key (16 bytes)
  ├─ 6. Decrypt file:
  │    └─ report.docx.enc --[AES-128]-> report.docx
  └─ 7. Lưu file gốc về máy
```

### Luồng 3: Share file (Re-wrapping)

```
┌─────────────────────────────────────────────────────────────────┐
│ 5. SHARE FILE (User A → User B)                                │
└─────────────────────────────────────────────────────────────────┘
Frontend (share_file_ui):
  ├─ 1. User A chọn file .enc
  ├─ 2. GET /api/file/list → Lấy fileId
  ├─ 3. Nhập email User B
  └─ 4. POST /api/file/share { fileId, recipientEmail }

Backend (shareFile):
  ├─ 1. Lấy file record của User A
  │    └─ file.aesKey = wrapped_key_A (base64)
  ├─ 2. Lấy recipient (User B) từ email
  │    └─ recipient.publicKey
  ├─ 3. Lấy sender.privateKey (User A)
  ├─ 4. Unwrap AES key:
  │    └─ aesKey = rsaDecrypt(wrapped_key_A, sender.privateKey)
  │         └─ → 16 bytes plaintext AES key
  ├─ 5. Re-wrap cho recipient:
  │    └─ wrapped_key_B = rsaEncrypt(aesKey, recipient.publicKey)
  │         └─ → 64 bytes mới
  ├─ 6. Tạo file record mới:
  │    └─ Files.create({
  │         userId: recipient.id,
  │         filename: "[Shared] report.docx",
  │         filePath: file.filePath,  ← Cùng file .enc
  │         aesKey: wrapped_key_B      ← Wrapped key MỚI
  │       })
  └─ 7. Response: { 
       error: 0, 
       sharedFile: { ..., aesKey: wrapped_key_B } 
     }

Frontend:
  ├─ 8. Nhận wrapped_key_B từ response
  ├─ 9. Decode base64 → binary (64 bytes)
  ├─ 10. Ghi vào file: report.docx.enc.key (OVERWRITE)
  └─ 11. Thông báo: "Gửi 2 file (.enc + .enc.key) cho User B"
```

### Luồng 4: Giải mã file được share

```
┌─────────────────────────────────────────────────────────────────┐
│ 6. GIẢI MÃ FILE ĐƯỢC SHARE (User B)                            │
└─────────────────────────────────────────────────────────────────┘
User B nhận 2 file từ User A:
  ├─ report.docx.enc (file encrypted, CÙNG với User A)
  └─ report.docx.enc.key (wrapped_key_B, KHÁC với User A)

Frontend (decrypt_shared_file):
  ├─ 1. Chọn file report.docx.enc
  ├─ 2. Tự động tìm report.docx.enc.key cùng thư mục
  ├─ 3. Nhập password
  ├─ 4. POST /api/user/get-private-key { password }
  │    └─ Backend trả privateKey_B của User B
  ├─ 5. Đọc wrapped_key_B từ file .enc.key (64 bytes binary)
  ├─ 6. Unwrap:
  │    └─ aesKey = open_aes_key(wrapped_key_B, privateKey_B)
  │         └─ → 16 bytes (CÙNG với User A unwrap ra)
  ├─ 7. Decrypt:
  │    └─ report.docx.enc --[AES-128]-> report.docx
  └─ 8. Lưu file gốc về máy

KẾT QUẢ:
  ✅ User A và User B đều giải mã được CÙNG file gốc
  ✅ Mỗi người dùng private key riêng
  ✅ File .enc không cần share nhiều lần
```

## 🧪 Testing & Debug

### 1. Test backend API
```bash
cd frontend/pyqt
python test_backend.py
```

### 2. Test crypto functions
```python
# Test AES encryption/decryption
from crypto.aes_encrypt import encrypt_file_data
from crypto.aes_decrypt import decrypt_file_data
import base64, secrets

data = b"Hello World"
aes_key = base64.b64encode(secrets.token_bytes(16)).decode()

encrypted = encrypt_file_data(data, aes_key)
decrypted = decrypt_file_data(encrypted, aes_key)
assert data == decrypted

# Test RSA wrap/unwrap
from crypto.cryptoRSA_test.rsa_wrap_key import seal_aes_key, open_aes_key

public_key = "n,e"  # Your RSA public key
private_key = "n,d" # Your RSA private key

wrapped = seal_aes_key(aes_key, public_key)
unwrapped = open_aes_key(wrapped, private_key)
assert aes_key == unwrapped
```

### 3. Debug logs

**Frontend**: Xem log trong app
```python
self.add_log(f"DEBUG: AES key = {aes_key}")
```

**Backend**: Console log
```javascript
console.log("🔍 DEBUG: Decrypted AES key:", aesKeyBuffer.toString('hex'));
```

### 4. Common issues

**❌ "Bad PKCS#7 padding bytes"**
- Nguyên nhân: AES key sai hoặc file .enc bị corrupt
- Fix: Kiểm tra unwrap logic, đảm bảo 16 bytes

**❌ "File không tồn tại"**
- Nguyên nhân: fileId sai hoặc không có quyền truy cập
- Fix: Kiểm tra userId trong JWT token

**❌ "Không lấy được private key"**
- Nguyên nhân: Password sai
- Fix: Nhập đúng password đã đăng ký

## ⚙️ Cấu hình

### Frontend (`frontend/pyqt/utils/config.py`):
```python
API_BASE_URL = "http://localhost:5000/api"  # Backend URL
DEMO_MODE = False                           # Set True để test UI
```

### Backend (`backend/config/config.js`):
```javascript
module.exports = {
  development: {
    dialect: 'sqlite',
    storage: './database.sqlite'
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: '24h'
  }
}
```

### Environment variables (`backend/.env`):
```bash
PORT=5000
JWT_SECRET=your_secret_key_here
DB_PATH=./database.sqlite
```