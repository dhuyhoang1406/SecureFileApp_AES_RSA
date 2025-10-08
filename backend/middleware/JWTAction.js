import jwt from "jsonwebtoken";
import { get_publicKey_Token } from "../services/user.js";

const JWTAction = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(" ")[1];
    const id_user = req.headers["x-user-id"];

    if (!token || !id_user)
      return res.status(401).json({ error: 2, message: "Unauthorized" });

    const publicKeyRes = await get_publicKey_Token(id_user);
    if (publicKeyRes.error === 1)
      return res.status(401).json({ error: 2, message: "Unauthorized" });

    jwt.verify(token, publicKeyRes.publicKey, (err, data) => {
      if (err) return res.status(401).json({ error: 2, message: "Unauthorized" });
      req.data = data;
      next();
    });
  } catch {
    return res.status(401).json({ error: 2, message: "Unauthorized" });
  }
};

export default JWTAction;
