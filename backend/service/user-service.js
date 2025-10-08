import bcrypt from "bcrypt";
import { User } from "../models/index.js";

const saltRounds = 10;

export const setPublicKey_Token = async (id, publicKey) => {
  const [updated] = await User.update({ publicKey }, { where: { id } });
  return {
    error: updated ? 0 : 1,
    message: updated ? "Cập nhật public key thành công" : "Thất bại",
  };
};

export const get_publicKey_Token = async (id) => {
  const user = await User.findByPk(id);
  if (!user) return { error: 1, message: "User not found" };
  return { error: 0, publicKey: user.publicKey };
};

export const changePassword = async (id, password, newPassword) => {
  const user = await User.findByPk(id);
  if (!user) return { error: 1, message: "Không tìm thấy user" };

  const match = bcrypt.compareSync(password, user.password);
  if (!match)
    return { error: 1, message: "Mật khẩu cũ không chính xác" };

  user.password = bcrypt.hashSync(newPassword, saltRounds);
  await user.save();
  return { error: 0, message: "Đổi mật khẩu thành công" };
};

export const save_Key = async (id, privateKey_rsa, key_aes) => {
  const [updated] = await User.update(
    { privateKey: privateKey_rsa, aesKey: key_aes },
    { where: { id } }
  );
  return {
    error: updated ? 0 : 1,
    message: updated ? "Lưu key thành công" : "Lưu key thất bại",
  };
};

export const get_Key = async (id) => {
  const user = await User.findByPk(id, { attributes: ["privateKey", "aesKey"] });
  if (!user) return { error: 1, message: "User not found" };
  return { error: 0, privateKey: user.privateKey, aesKey: user.aesKey };
};
