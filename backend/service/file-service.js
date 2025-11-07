import { File } from "../models/index.js";

export const uploadFile = async (userId, filename, filePath, aesKey) => {
  const file = await File.create({ filename, filePath, aesKey, userId });
  return { error: 0, message: "Tải lên thành công", file };
};

export const getFiles = async (userId) => {
  const files = await File.findAll({ where: { userId } });
  return { error: 0, files };
};

export const getFileById = async (fileId, userId) => {
  const file = await File.findOne({
    where: { id: fileId, userId },
  });
  return file;
};

export const createSharedFile = async (
  recipientId,
  filename,
  filePath,
  encryptedAesKey,
  sharedBy
) => {
  const file = await File.create({
    userId: recipientId,
    filename: `[Shared] ${filename}`,
    filePath: filePath,
    aesKey: encryptedAesKey,
    // Có thể thêm field sharedBy để track ai share
  });
  return file;
};
