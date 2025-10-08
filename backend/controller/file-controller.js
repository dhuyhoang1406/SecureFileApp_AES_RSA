import * as fileServices from "../services/file.js";

export const upload = async (req, res) => {
  const id = req.data.id;
  const { filename, filePath, aesKey } = req.body;
  if (!filename || !filePath || !aesKey)
    return res.status(400).json({ error: 1, message: "Thiếu thông tin" });

  const response = await fileServices.uploadFile(id, filename, filePath, aesKey);
  return res.status(200).json(response);
};

export const getFiles = async (req, res) => {
  const id = req.data.id;
  const response = await fileServices.getFiles(id);
  return res.status(200).json(response);
};
