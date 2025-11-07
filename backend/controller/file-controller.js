import * as fileServices from "../service/file-service.js";
import { User } from "../models/index.js";
import { rsaEncrypt, rsaDecrypt } from "../utils/crypto-helper.js";

export const upload = async (req, res) => {
  const id = req.data.id;
  const { filename, filePath, aesKey } = req.body;
  console.log("Received upload request:", { filename, filePath, aesKey });
  if (!filename || !filePath || !aesKey)
    return res.status(400).json({ error: 1, message: "Thiếu thông tin" });

  const response = await fileServices.uploadFile(
    id,
    filename,
    filePath,
    aesKey
  );
  return res.status(200).json(response);
};

export const getFiles = async (req, res) => {
  const id = req.data.id;
  const response = await fileServices.getFiles(id);
  return res.status(200).json(response);
};

/**
 * Share file với user khác
 * POST /api/file/share
 * Body: { fileId: number, recipientEmail: string }
 *
 * Logic:
 * 1. Lấy file record của người gửi (có encrypted AES key)
 * 2. Giải mã AES key bằng private key của người gửi
 * 3. Mã hóa lại AES key bằng public key của người nhận
 * 4. Tạo file record mới cho người nhận với encrypted key mới
 */
export const shareFile = async (req, res) => {
  try {
    const senderId = req.data.id;
    const { fileId, recipientEmail } = req.body;

    if (!fileId || !recipientEmail) {
      return res.status(400).json({
        error: 1,
        message: "Thiếu thông tin fileId hoặc recipientEmail",
      });
    }

    // 1. Lấy thông tin file của sender
    const file = await fileServices.getFileById(fileId, senderId);
    if (!file) {
      return res.status(404).json({
        error: 1,
        message: "File không tồn tại hoặc bạn không có quyền truy cập",
      });
    }

    // 2. Lấy thông tin recipient
    const recipient = await User.findOne({
      where: { email: recipientEmail },
      attributes: ["id", "publicKey"],
    });
    if (!recipient) {
      return res
        .status(404)
        .json({ error: 1, message: "Người nhận không tồn tại" });
    }

    if (recipient.id === senderId) {
      return res
        .status(400)
        .json({ error: 1, message: "Không thể share file cho chính mình" });
    }

    // 3. Lấy private key của sender để giải mã AES key
    const sender = await User.findByPk(senderId, {
      attributes: ["privateKey"],
    });
    if (!sender.privateKey) {
      return res
        .status(400)
        .json({ error: 1, message: "Sender không có private key" });
    }

    // 4. Giải mã AES key (file.aesKey đang lưu dạng base64 của encrypted key)
    const encryptedAesKeyBuffer = Buffer.from(file.aesKey, "base64");
    console.log("🔍 DEBUG: Encrypted AES key (base64):", file.aesKey);
    console.log(
      "🔍 DEBUG: Encrypted AES key buffer length:",
      encryptedAesKeyBuffer.length
    );

    const aesKeyBuffer = rsaDecrypt(encryptedAesKeyBuffer, sender.privateKey);
    console.log("🔍 DEBUG: Decrypted AES key length:", aesKeyBuffer.length);
    console.log(
      "🔍 DEBUG: Decrypted AES key (hex):",
      aesKeyBuffer.toString("hex")
    );

    // 5. Mã hóa lại AES key bằng public key của recipient
    const newEncryptedAesKey = rsaEncrypt(aesKeyBuffer, recipient.publicKey);
    console.log(
      "🔍 DEBUG: New encrypted AES key length:",
      newEncryptedAesKey.length
    );
    const newEncryptedAesKeyBase64 = newEncryptedAesKey.toString("base64");
    console.log(
      "🔍 DEBUG: New encrypted AES key (base64):",
      newEncryptedAesKeyBase64
    );

    // 6. Tạo file record mới cho recipient
    const sharedFile = await fileServices.createSharedFile(
      recipient.id,
      file.filename,
      file.filePath,
      newEncryptedAesKeyBase64,
      senderId
    );

    return res.status(200).json({
      error: 0,
      message: `File đã được chia sẻ với ${recipientEmail}`,
      sharedFile,
    });
  } catch (error) {
    console.error("shareFile error:", error);
    return res
      .status(500)
      .json({ error: 1, message: "Internal server error: " + error.message });
  }
};

/**
 * Tải wrapped key của file dưới dạng file .enc.key (để giải mã)
 * GET /api/file/:fileId/download-key
 * Trả về file .enc.key (binary download) chứa wrapped AES key
 */
export const downloadKey = async (req, res) => {
  try {
    const userId = req.data.id;
    const { fileId } = req.params;

    if (!fileId) {
      return res.status(400).json({ error: 1, message: "File ID is required" });
    }

    // Lấy file của user
    const file = await fileServices.getFileById(fileId, userId);
    if (!file) {
      return res.status(404).json({
        error: 1,
        message: "File không tồn tại hoặc bạn không có quyền truy cập",
      });
    }

    // Chuyển wrapped key từ base64 về binary
    const wrappedKeyBuffer = Buffer.from(file.aesKey, "base64");

    // Set headers để download file
    res.setHeader("Content-Type", "application/octet-stream");
    res.setHeader(
      "Content-Disposition",
      `attachment; filename="${file.filename}.enc.key"`
    );
    res.setHeader("Content-Length", wrappedKeyBuffer.length);

    // Gửi binary data
    return res.status(200).send(wrappedKeyBuffer);
  } catch (error) {
    console.error("downloadKey error:", error);
    return res
      .status(500)
      .json({ error: 1, message: "Internal server error: " + error.message });
  }
};

/**
 * Tải nội dung file đã mã hóa
 * GET /api/file/:fileId/download
 * Trả về nội dung file đã mã hóa (base64)
 */
export const downloadFile = async (req, res) => {
  try {
    const userId = req.data.id;
    const { fileId } = req.params;

    if (!fileId) {
      return res.status(400).json({ error: 1, message: "File ID is required" });
    }

    // Lấy file của user
    const file = await fileServices.getFileById(fileId, userId);
    if (!file) {
      return res.status(404).json({
        error: 1,
        message: "File không tồn tại hoặc bạn không có quyền truy cập",
      });
    }

    // Đọc file từ disk
    const fs = await import("fs");
    const path = await import("path");

    // filePath có thể là relative hoặc absolute
    let fullPath = file.filePath;
    if (!path.isAbsolute(fullPath)) {
      // Nếu là relative path, join với thư mục gốc của project
      fullPath = path.join(process.cwd(), fullPath);
    }

    if (!fs.existsSync(fullPath)) {
      return res
        .status(404)
        .json({ error: 1, message: "File vật lý không tồn tại trên server" });
    }

    const fileContent = fs.readFileSync(fullPath);
    const fileContentBase64 = fileContent.toString("base64");

    return res.status(200).json({
      error: 0,
      data: {
        content: fileContentBase64,
        filename: file.filename,
      },
    });
  } catch (error) {
    console.error("downloadFile error:", error);
    return res
      .status(500)
      .json({ error: 1, message: "Internal server error: " + error.message });
  }
};
