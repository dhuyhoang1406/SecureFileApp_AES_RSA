import { Router } from "express";
import * as authController from "../controllers/auth.js";
import * as userController from "../controllers/user.js";
import * as fileController from "../controllers/file.js";
import JWTAction from "../middleware/JWTAction.js";

const route = Router();

route.post("/auth/register", authController.register);
route.post("/auth/login", authController.login);

route.use(JWTAction);
route.put("/user/change-password", userController.changePassword);
route.post("/user/save-key", userController.save_Key);
route.get("/user/get-key", userController.get_Key);

route.post("/file/upload", fileController.upload);
route.get("/file/list", fileController.getFiles);

export default route;
