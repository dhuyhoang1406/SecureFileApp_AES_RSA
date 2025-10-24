# aes_decrypt.py
# Decrypt pipeline: RSA unwrap AES key (Base64) -> AES-ECB decrypt (PKCS#7)

import base64
from typing import List

# Dùng lại các hàm từ encrypt side (ECB + PKCS#7)  :contentReference[oaicite:2]{index=2}
from aes_encrypt import key_expansion, add_round_key

# ===== RSA unwrap theo format rsa_wrap_key.py (file key Base64, private key "n,d")  :contentReference[oaicite:3]{index=3}
def rsa_decrypt(cipher: bytes, n: int, d: int) -> bytes:
    c = int.from_bytes(cipher, "big")
    m = pow(c, d, n)
    return m.to_bytes((m.bit_length() + 7) // 8, "big")

# ===== Inverse AES primitives (ECB decrypt) =====
INV_S_BOX = [
    0x52,0x09,0x6a,0xd5,0x30,0x36,0xa5,0x38,0xbf,0x40,0xa3,0x9e,0x81,0xf3,0xd7,0xfb,
    0x7c,0xe3,0x39,0x82,0x9b,0x2f,0xff,0x87,0x34,0x8e,0x43,0x44,0xc4,0xde,0xe9,0xcb,
    0x54,0x7b,0x94,0x32,0xa6,0xc2,0x23,0x3d,0xee,0x4c,0x95,0x0b,0x42,0xfa,0xc3,0x4e,
    0x08,0x2e,0xa1,0x66,0x28,0xd9,0x24,0xb2,0x76,0x5b,0xa2,0x49,0x6d,0x8b,0xd1,0x25,
    0x72,0xf8,0xf6,0x64,0x86,0x68,0x98,0x16,0xd4,0xa4,0x5c,0xcc,0x5d,0x65,0xb6,0x92,
    0x6c,0x70,0x48,0x50,0xfd,0xed,0xb9,0xda,0x5e,0x15,0x46,0x57,0xa7,0x8d,0x9d,0x84,
    0x90,0xd8,0xab,0x00,0x8c,0xbc,0xd3,0x0a,0xf7,0xe4,0x58,0x05,0xb8,0xb3,0x45,0x06,
    0xd0,0x2c,0x1e,0x8f,0xca,0x3f,0x0f,0x02,0xc1,0xaf,0xbd,0x03,0x01,0x13,0x8a,0x6b,
    0x3a,0x91,0x11,0x41,0x4f,0x67,0xdc,0xea,0x97,0xf2,0xcf,0xce,0xf0,0xb4,0xe6,0x73,
    0x96,0xac,0x74,0x22,0xe7,0xad,0x35,0x85,0xe2,0xf9,0x37,0xe8,0x1c,0x75,0xdf,0x6e,
    0x47,0xf1,0x1a,0x71,0x1d,0x29,0xc5,0x89,0x6f,0xb7,0x62,0x0e,0xaa,0x18,0xbe,0x1b,
    0xfc,0x56,0x3e,0x4b,0xc6,0xd2,0x79,0x20,0x9a,0xdb,0xc0,0xfe,0x78,0xcd,0x5a,0xf4,
    0x1f,0xdd,0xa8,0x33,0x88,0x07,0xc7,0x31,0xb1,0x12,0x10,0x59,0x27,0x80,0xec,0x5f,
    0x60,0x51,0x7f,0xa9,0x19,0xb5,0x4a,0x0d,0x2d,0xe5,0x7a,0x9f,0x93,0xc9,0x9c,0xef,
    0xa0,0xe0,0x3b,0x4d,0xae,0x2a,0xf5,0xb0,0xc8,0xeb,0xbb,0x3c,0x83,0x53,0x99,0x61,
    0x17,0x2b,0x04,0x7e,0xba,0x77,0xd6,0x26,0xe1,0x69,0x14,0x63,0x55,0x21,0x0c,0x7d
]

def inv_sub_bytes(state: list[int]) -> list[int]:
    return [INV_S_BOX[b] for b in state]

def inv_shift_rows(state: list[int]) -> list[int]:
    return [
        state[0], state[13], state[10], state[7],
        state[4], state[1],  state[14], state[11],
        state[8], state[5],  state[2],  state[15],
        state[12],state[9],  state[6],  state[3]
    ]

def xtime(a: int) -> int:
    return ((a << 1) & 0xFF) ^ (0x1B if (a & 0x80) else 0x00)

def gf_mul(a: int, b: int) -> int:
    res = 0
    for _ in range(8):
        if b & 1:
            res ^= a
        a = xtime(a)
        b >>= 1
    return res & 0xFF

def inv_mix_columns(state: list[int]) -> list[int]:
    out = []
    for i in range(4):
        c0,c1,c2,c3 = state[i*4:(i+1)*4]
        out += [
            (gf_mul(c0,14) ^ gf_mul(c1,11) ^ gf_mul(c2,13) ^ gf_mul(c3, 9)) & 0xFF,
            (gf_mul(c0, 9) ^ gf_mul(c1,14) ^ gf_mul(c2,11) ^ gf_mul(c3,13)) & 0xFF,
            (gf_mul(c0,13) ^ gf_mul(c1, 9) ^ gf_mul(c2,14) ^ gf_mul(c3,11)) & 0xFF,
            (gf_mul(c0,11) ^ gf_mul(c1,13) ^ gf_mul(c2, 9) ^ gf_mul(c3,14)) & 0xFF
        ]
    return out

def aes_decrypt_block(block: bytes, key_schedule: list[list[int]], Nr: int) -> bytes:
    state = list(block)
    # Add round key cuối (w[40..43] với AES-128)
    state = add_round_key(state, sum(key_schedule[Nr*4:(Nr+1)*4], []))
    # Vòng cuối (không có InvMixColumns)
    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    # Các vòng trung gian (có InvMixColumns)
    for rnd in range(Nr-1, 0, -1):
        state = add_round_key(state, sum(key_schedule[rnd*4:(rnd+1)*4], []))
        state = inv_mix_columns(state)
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
    # Vòng đầu
    state = add_round_key(state, sum(key_schedule[0:4], []))
    return bytes(state)

def pkcs7_unpad(data: bytes) -> bytes:
    if not data or len(data) % 16 != 0:
        raise ValueError("Ciphertext size invalid")
    pad = data[-1]
    if pad == 0 or pad > 16:
        raise ValueError("Bad PKCS#7 padding length")
    if data[-pad:] != bytes([pad]) * pad:
        raise ValueError("Bad PKCS#7 padding bytes")
    return data[:-pad]

# ===== API 1: Decrypt với RSA key file (khớp rsa_wrap_key.py) =====
def decrypt_file_with_rsa_key(enc_path: str, out_path: str, enc_key_path: str, rsa_private_txt: str) -> None:
    """
    enc_path: file dữ liệu .enc (AES-ECB + PKCS7)
    out_path: file xuất plaintext
    enc_key_path: file chứa AES key đã ENCRYPT bằng RSA (Base64)
    rsa_private_txt: file text "n,d" (giống rsa_wrap_key.py)
    """
    # 1) RSA unwrap khóa AES (Base64 -> bytes -> RSA decrypt -> 16B)
    enc_key_b64 = open(enc_key_path, "rb").read()
    enc_key = base64.b64decode(enc_key_b64)
    n, d = map(int, open(rsa_private_txt, "r").read().split(","))
    aes_key = rsa_decrypt(enc_key, n, d).rjust(16, b"\x00")  # AES-128 theo rsa_wrap_key.py

    # 2) Key schedule từ encrypt side  :contentReference[oaicite:4]{index=4}
    key_schedule, Nr = key_expansion(aes_key)  # với 16B -> Nr = 10

    # 3) Đọc và giải mã theo block
    ct = open(enc_path, "rb").read()
    if len(ct) % 16 != 0:
        raise ValueError("Ciphertext length must be multiple of 16 for ECB")
    pt_chunks = []
    for i in range(0, len(ct), 16):
        pt_chunks.append(aes_decrypt_block(ct[i:i+16], key_schedule, Nr))
    pt = b"".join(pt_chunks)

    # 4) Gỡ PKCS#7  :contentReference[oaicite:5]{index=5}
    pt = pkcs7_unpad(pt)

    # 5) Ghi file
    with open(out_path, "wb") as f:
        f.write(pt)

# ===== API 2: Decrypt khi đã có AES key plaintext (không cần RSA) =====
def decrypt_file_with_plain_key(enc_path: str, out_path: str, aes_key: bytes) -> None:
    key_schedule, Nr = key_expansion(aes_key)
    ct = open(enc_path, "rb").read()
    if len(ct) % 16 != 0:
        raise ValueError("Ciphertext length must be multiple of 16 for ECB")
    pt_chunks = []
    for i in range(0, len(ct), 16):
        pt_chunks.append(aes_decrypt_block(ct[i:i+16], key_schedule, Nr))
    pt = pkcs7_unpad(b"".join(pt_chunks))
    with open(out_path, "wb") as f:
        f.write(pt)

# Demo nhanh (tuỳ chọn)
if __name__ == "__main__":
    # Test decrypt với RSA wrapped key
    decrypt_file_with_rsa_key(
        enc_path="test.enc",
        out_path="test.dec.txt",
        enc_key_path="aes.key.enc",
        rsa_private_txt="rsa_prv.txt",
    )
    print("Decrypt xong: test.dec.txt")
    
    # Test 2: Decrypt với RSA wrapped key
    # decrypt_file_with_rsa_key(
    #     enc_path="test.enc",
    #     out_path="test.dec2.txt",
    #     enc_key_path="aes.key.enc",
    #     rsa_private_txt="rsa_prv.txt",
    # )
    # print("✅ Decrypt xong: test.dec2.txt")
