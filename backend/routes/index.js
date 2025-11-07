import { Router } from "express";
import * as authController from "../controller/auth-controller.js";
import * as userController from "../controller/user-controller.js";
import * as fileController from "../controller/file-controller.js";
import JWTAction from "../middleware/JWTAction.js";

const route = Router();

route.post("/auth/register", authController.register);
route.post("/auth/login", authController.login);
route.post("/auth/logout", authController.logout);

route.use(JWTAction);
route.put("/user/change-password", userController.changePassword);
route.post("/user/save-key", userController.saveKey);
route.get("/user/get-key", userController.getKey);
route.post("/user/get-private-key", userController.getPrivateKey); // Endpoint mới - yêu cầu password

route.post("/file/upload", fileController.upload);
route.get("/file/list", fileController.getFiles);
route.post("/file/share", fileController.shareFile); // Endpoint share file
route.get("/file/:fileId/download-key", fileController.downloadKey); // Endpoint download wrapped key
route.get("/file/:fileId/download", fileController.downloadFile); // Endpoint download file content

export default route;
