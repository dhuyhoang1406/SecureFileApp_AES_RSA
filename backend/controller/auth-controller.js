import * as authServices from "../services/auth.js";
import * as userServices from "../services/user.js";
import create_token from "../utils/create-token.js";
import * as regex from "../utils/regex.js";

export const register = async (req, res) => {
  const { email, password, repeatPassword } = req.body;
  if (!email || !password || !repeatPassword)
    return res.status(400).json({ error: 1, message: "Thiếu thông tin" });

  if (!regex.rgEmail.test(email))
    return res.status(400).json({ error: 1, message: "Email không hợp lệ" });

  if (password !== repeatPassword)
    return res.status(400).json({ error: 1, message: "Mật khẩu xác nhận sai" });

  const response = await authServices.register(email, password);
  return res.status(200).json(response);
};

export const login = async (req, res) => {
  const { email, password } = req.body;
  const response = await authServices.login(email, password);
  if (response.error === 1) return res.status(401).json(response);

  const accessToken = create_token(response.id);
  await userServices.setPublicKey_Token(response.id, accessToken.public_key_token);

  return res.status(200).json({
    error: 0,
    message: "Đăng nhập thành công",
    token: accessToken.token,
    userId: response.id,
  });
};
