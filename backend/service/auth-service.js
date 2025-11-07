import bcrypt from "bcrypt";
import { User } from "../models/index.js";
import { generateRSAKeypair } from "../utils/crypto-helper.js";
const saltRounds = 10;

export const register = async (email, password) => {
  const existing = await User.findOne({ where: { email } });
  if (existing) return { error: 1, message: "Email đã tồn tại" };

  // Tự động tạo RSA keypair cho user mới (512-bit cho demo, nên dùng 2048+ production)
  const { publicKey, privateKey } = generateRSAKeypair(512);

  await User.create({
    email,
    username: email.split("@")[0],
    password: bcrypt.hashSync(password, saltRounds),
    publicKey, // Lưu public key "n,e"
    privateKey, // Lưu private key "n,d" (sẽ được bảo vệ bởi password verification)
  });

  return { error: 0, message: "Đăng ký thành công" };
};

export const login = async (email, password) => {
  const user = await User.findOne({ where: { email } });
  if (!user)
    return { error: 1, message: "Email hoặc mật khẩu không chính xác" };

  const match = bcrypt.compareSync(password, user.password);
  if (!match)
    return { error: 1, message: "Email hoặc mật khẩu không chính xác" };

  return { error: 0, message: "Đăng nhập thành công", id: user.id };
};

const blacklist = new Set();
export const invalidateToken = async (token) => {
  blacklist.add(token);
};

export const isTokenBlacklisted = (token) => {
  return blacklist.has(token);
};
