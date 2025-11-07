import secrets, base64, os, sys

# Force UTF-8 output (an toan hon neu muon giu ky tu dac biet)
sys.stdout.reconfigure(encoding='utf-8')

# ===== 1. BASIC FUNCTIONS =====

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("No modular inverse exists!")
    return x % m

# ===== 2. PRIME GENERATION =====

def is_probable_prime(n, k=16):
    if n < 2:
        return False
    # quick small prime check
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write n-1 = d * 2^r
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    # Miller–Rabin
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2  # a in [2, n-2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def gen_prime(bits=256):
    while True:
        # ensure high bit and odd
        x = (secrets.randbits(bits) | (1 << (bits - 1)) | 1)
        if is_probable_prime(x):
            return x

# ===== 3. RSA KEY GENERATION =====

def keygen(bits=512):
    p = gen_prime(bits // 2)
    q = gen_prime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while gcd(e, phi) != 1:
            e += 2
    d = modinv(e, phi)
    return n, e, d

# ===== 4. RSA ENCRYPTION / DECRYPTION =====

def rsa_encrypt(data: bytes, n, e):
    m = int.from_bytes(data, "big")
    c = pow(m, e, n)
    return c.to_bytes((c.bit_length() + 7) // 8, "big")

def rsa_decrypt(cipher: bytes, n, d):
    c = int.from_bytes(cipher, "big")
    m = pow(c, d, n)
    return m.to_bytes((m.bit_length() + 7) // 8, "big")

# ===== 5. WRAP AES KEY (DEMO) =====

def seal_key(aes_path, pub_file, out_file):
    key = open(aes_path, "rb").read()
    if len(key) != 16:
        raise ValueError("AES-128 key must be 16 bytes!")
    n, e = map(int, open(pub_file).read().split(","))
    enc = rsa_encrypt(key, n, e)
    open(out_file, "wb").write(base64.b64encode(enc))
    print("Encrypted AES key saved to", out_file)

def open_key(enc_path, prv_file, out_file):
    enc = base64.b64decode(open(enc_path, "rb").read())
    n, d = map(int, open(prv_file).read().split(","))
    dec = rsa_decrypt(enc, n, d)
    dec = dec.rjust(16, b"\x00")  # ensure 16 bytes
    open(out_file, "wb").write(dec)
    print("Decrypted AES key saved to", out_file)

def seal_aes_key(aes_key_bytes: bytes, public_key_str: str) -> bytes:
    n, e = map(int, public_key_str.split(','))
    m = int.from_bytes(aes_key_bytes, 'big')
    c = pow(m, e, n)
    return c.to_bytes((c.bit_length() + 7) // 8, 'big')

def open_aes_key(encrypted_key_bytes: bytes, private_key_str: str) -> bytes:
    """
    Unwrap AES key từ RSA encrypted bytes
    Returns: 16 bytes AES key
    """
    n, d = map(int, private_key_str.split(','))
    c = int.from_bytes(encrypted_key_bytes, 'big')
    m = pow(c, d, n)
    
    # Tính số bytes cần thiết dựa trên bit_length của m
    num_bytes = (m.bit_length() + 7) // 8
    
    # Nếu m = 0, trả về 16 bytes zero
    if m == 0:
        return b'\x00' * 16
    
    key = m.to_bytes(num_bytes, 'big')
    
    # Nếu key đã đúng 16 bytes hoặc ít hơn, pad về 16 bytes
    if len(key) <= 16:
        return key.rjust(16, b'\x00')
    
    # Nếu key dài hơn 16 bytes, có thể có padding zeros phía trước
    # Chỉ strip tối đa để còn lại 16 bytes
    while len(key) > 16 and key[0] == 0:
        key = key[1:]
    
    # Nếu vẫn dài hơn 16 bytes (không nên xảy ra với AES-128)
    if len(key) > 16:
        # Lấy 16 bytes cuối
        key = key[-16:]
    
    return key.rjust(16, b'\x00')

if __name__ == "__main__":
    print("Generating RSA keypair...", flush=True)
    n, e, d = keygen(512)
    open("rsa_pub.txt", "w").write(f"{n},{e}")
    open("rsa_prv.txt", "w").write(f"{n},{d}")
    print("RSA keys generated! (rsa_pub.txt / rsa_prv.txt)", flush=True)

    # Create AES key if not exists
    if not os.path.exists("aes.key"):
        open("aes.key", "wb").write(os.urandom(16))
        print("Created sample aes.key (16 bytes)")

    # Encrypt and decrypt AES key
    seal_key("aes.key", "rsa_pub.txt", "aes.key.enc")
    open_key("aes.key.enc", "rsa_prv.txt", "aes.key.dec")

    same = open("aes.key", "rb").read() == open("aes.key.dec", "rb").read()
    print("Compare original vs decrypted:", same)
