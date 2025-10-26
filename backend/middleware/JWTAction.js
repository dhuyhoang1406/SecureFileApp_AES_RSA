import jwt from "jsonwebtoken";
import { get_publicKey_Token } from "../service/user-service.js";
import { isTokenBlacklisted } from "../service/auth-service.js";

const JWTAction = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(" ")[1];
    const id_user = req.headers["x-user-id"];

    if (!token || !id_user)
      return res.status(401).json({ error: 2, message: "Unauthorized" });

    // Kiểm tra token trong blacklist
    if (await isTokenBlacklisted(token))
      return res.status(401).json({ error: 2, message: "Unauthorized" });

    const publicKeyRes = await get_publicKey_Token(id_user);
    if (publicKeyRes.error === 1)
      return res.status(401).json({ error: 2, message: "Unauthorized" });

    jwt.verify(token, publicKeyRes.publicKey, (err, data) => {
      if (err) {
        console.error("JWTAction - JWT verification error:", err);

        if (err.name === "TokenExpiredError") {
          return res.status(401).json({
            error: 3,
            message: "Token expired",
            expiredAt: err.expiredAt,
          });
        }

        // Token không hợp lệ
        return res.status(401).json({
          error: 2,
          message: "Unauthorized",
        });
      }

      req.data = data;
      next();
    });
  } catch (error) {
    console.error("JWTAction - error:", error);
    return res.status(401).json({ error: 2, message: "Unauthorized" });
  }
};

export default JWTAction;
