/**
 * Crypto helper functions for RSA key generation (compatible with Python RSA format)
 * Format: "n,e" for public key, "n,d" for private key
 */

// Simple GCD
function gcd(a, b) {
  while (b !== 0n) {
    [a, b] = [b, a % b];
  }
  return a;
}

// Extended GCD
function egcd(a, b) {
  if (b === 0n) {
    return [a, 1n, 0n];
  }
  const [g, x1, y1] = egcd(b, a % b);
  return [g, y1, x1 - (a / b) * y1];
}

// Modular inverse
function modinv(a, m) {
  const [g, x] = egcd(a, m);
  if (g !== 1n) {
    throw new Error("No modular inverse exists");
  }
  return ((x % m) + m) % m;
}

// Miller-Rabin primality test
function isProbablePrime(n, k = 16) {
  if (n < 2n) return false;
  if (n === 2n || n === 3n) return true;
  if (n % 2n === 0n) return false;

  // Write n-1 as d * 2^r
  let r = 0n;
  let d = n - 1n;
  while (d % 2n === 0n) {
    r++;
    d /= 2n;
  }

  // Witness loop
  for (let i = 0; i < k; i++) {
    const a = randomBigInt(2n, n - 2n);
    let x = modPow(a, d, n);

    if (x === 1n || x === n - 1n) continue;

    let continueWitnessLoop = false;
    for (let j = 0n; j < r - 1n; j++) {
      x = modPow(x, 2n, n);
      if (x === n - 1n) {
        continueWitnessLoop = true;
        break;
      }
    }
    if (continueWitnessLoop) continue;
    return false;
  }
  return true;
}

// Generate random BigInt in range [min, max]
function randomBigInt(min, max) {
  const range = max - min;
  const bits = range.toString(2).length;
  let result;
  do {
    result = BigInt("0x" + randomHex(Math.ceil(bits / 4)));
  } while (result > range);
  return result + min;
}

// Generate random hex string
import crypto from "crypto";
function randomHex(length) {
  return crypto
    .randomBytes(Math.ceil(length / 2))
    .toString("hex")
    .slice(0, length);
}

// Modular exponentiation
function modPow(base, exp, mod) {
  let result = 1n;
  base = base % mod;
  while (exp > 0n) {
    if (exp % 2n === 1n) {
      result = (result * base) % mod;
    }
    exp = exp / 2n;
    base = (base * base) % mod;
  }
  return result;
}

// Generate prime number with given bit length
function genPrime(bits = 256) {
  const min = 1n << BigInt(bits - 1);
  const max = (1n << BigInt(bits)) - 1n;

  for (let attempts = 0; attempts < 1000; attempts++) {
    let candidate = randomBigInt(min, max);
    candidate |= 1n; // Make it odd

    if (isProbablePrime(candidate)) {
      return candidate;
    }
  }
  throw new Error("Failed to generate prime after 1000 attempts");
}

/**
 * Generate RSA keypair (512-bit for demo, use 2048+ in production)
 * Returns: { publicKey: "n,e", privateKey: "n,d" }
 */
export function generateRSAKeypair(bits = 512) {
  const p = genPrime(bits / 2);
  const q = genPrime(bits / 2);
  const n = p * q;
  const phi = (p - 1n) * (q - 1n);

  let e = 65537n;
  if (gcd(e, phi) !== 1n) {
    e = 3n;
    while (gcd(e, phi) !== 1n) {
      e += 2n;
    }
  }

  const d = modinv(e, phi);

  return {
    publicKey: `${n},${e}`,
    privateKey: `${n},${d}`,
  };
}

/**
 * Encrypt data with RSA public key (format: "n,e")
 */
export function rsaEncrypt(data, publicKeyStr) {
  const [n, e] = publicKeyStr.split(",").map((s) => BigInt(s));
  const m = BigInt("0x" + Buffer.from(data).toString("hex"));
  const c = modPow(m, e, n);
  return Buffer.from(c.toString(16).padStart(128, "0"), "hex");
}

/**
 * Decrypt data with RSA private key (format: "n,d")
 * Returns: Buffer (ALWAYS 16 bytes for AES-128 key)
 */
export function rsaDecrypt(cipherBuffer, privateKeyStr) {
  const [n, d] = privateKeyStr.split(",").map((s) => BigInt(s));
  const c = BigInt("0x" + cipherBuffer.toString("hex"));
  const m = modPow(c, d, n);

  // Convert BigInt to hex string
  let hex = m.toString(16);

  // Pad hex to even length (for Buffer.from)
  if (hex.length % 2 !== 0) {
    hex = "0" + hex;
  }

  // Convert to Buffer
  let keyBuffer = Buffer.from(hex, "hex");

  // ✅ PAD về đúng 16 bytes (giống Python)
  if (keyBuffer.length < 16) {
    // Pad với zeros ở đầu
    const padded = Buffer.alloc(16);
    keyBuffer.copy(padded, 16 - keyBuffer.length);
    return padded;
  } else if (keyBuffer.length > 16) {
    // Strip leading zeros nếu dài hơn 16 bytes
    while (keyBuffer.length > 16 && keyBuffer[0] === 0) {
      keyBuffer = keyBuffer.slice(1);
    }
    // Nếu vẫn > 16, lấy 16 bytes cuối
    if (keyBuffer.length > 16) {
      return keyBuffer.slice(-16);
    }
    // Nếu < 16 sau khi strip, pad lại
    if (keyBuffer.length < 16) {
      const padded = Buffer.alloc(16);
      keyBuffer.copy(padded, 16 - keyBuffer.length);
      return padded;
    }
  }

  return keyBuffer;
}
