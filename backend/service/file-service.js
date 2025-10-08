import { File } from "../models/index.js";

export const uploadFile = async (userId, filename, filePath, aesKey) => {
  const file = await File.create({ filename, filePath, aesKey, userId });
  return { error: 0, message: "Tải lên thành công", file };
};

export const getFiles = async (userId) => {
  const files = await File.findAll({ where: { userId } });
  return { error: 0, files };
};
