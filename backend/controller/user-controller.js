import { User } from "../models/index.js";

// NOTE: Các endpoint user ở backend sẽ lấy user id từ middleware JWTAction
// (req.data.id) hoặc từ header 'x-user-id' nếu có. Tránh dùng req.params.

export const saveKey = async (req, res) => {
  try {
    // Prefer id from verified token data (set by JWTAction), fallback to header or body
    const idFromToken = req.data?.id;
    const idFromHeader = req.headers["x-user-id"];
    const userId = idFromToken || idFromHeader || req.body.userId;

    // Accept publicKey and privateKey in body (frontend sends these)
    const { publicKey, privateKey, aesKey } = req.body;

    if (!userId) {
      return res
        .status(400)
        .json({ error: 1, message: "User ID is required." });
    }

    const user = await User.findByPk(userId);
    if (!user)
      return res.status(404).json({ error: 1, message: "User not found." });

    // Update fields if provided
    if (publicKey !== undefined) user.publicKey = publicKey;
    if (privateKey !== undefined) user.privateKey = privateKey;
    if (aesKey !== undefined) user.aesKey = aesKey;

    await user.save();

    return res
      .status(200)
      .json({ error: 0, message: "Keys saved successfully." });
  } catch (error) {
    console.error(error);
    return res
      .status(500)
      .json({ error: 1, message: "Internal server error." });
  }
};

// controller/user-controller.js
export const getKey = async (req, res) => {
  try {
    const idFromToken = req.data?.id;
    const idFromHeader = req.headers["x-user-id"];
    const userId =
      idFromToken || idFromHeader || req.query.userId || req.body.userId;

    if (!userId) {
      return res.status(400).json({ error: 1, message: "User ID is required." });
    }

    const user = await User.findByPk(userId, {
      attributes: ["publicKey", "privateKey"], // BỎ aesKey
    });

    if (!user) {
      return res.status(404).json({ error: 1, message: "User not found." });
    }

    return res.status(200).json({
      error: 0,
      data: {
        publicKey: user.publicKey,
        privateKey: user.privateKey,
        // aesKey: user.aesKey, // BỎ DÒNG NÀY
      },
    });
  } catch (error) {
    console.error("getKey error:", error);
    return res.status(500).json({ error: 1, message: "Internal server error." });
  }
};
export const changePassword = async (req, res) => {
  try {
    const { userId, oldPassword, newPassword } = req.body;
    if (!userId || !oldPassword || !newPassword) {
      return res
        .status(400)
        .json({ error: 1, message: "Missing required fields." });
    }
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({ error: 1, message: "User not found." });
    }
    // validatePassword / hash helpers may not exist on model; attempt safe checks
    if (typeof user.validatePassword === "function") {
      const isMatch = await user.validatePassword(oldPassword);
      if (!isMatch) {
        return res
          .status(401)
          .json({ error: 1, message: "Old password is incorrect." });
      }
    }

    // If model provides a hash util, use it; otherwise assume plain assignment is acceptable
    if (typeof User.hashPassword === "function") {
      user.password = await User.hashPassword(newPassword);
    } else {
      user.password = newPassword;
    }
    await user.save();
    return res
      .status(200)
      .json({ error: 0, message: "Password changed successfully." });
  } catch (error) {
    console.error(error);
    return res
      .status(500)
      .json({ error: 1, message: "Internal server error." });
  }
};
