// utils/create-token.js
import jwt from "jsonwebtoken";
import fs from "fs";
import path from "path";

const JWT_PRIVATE_KEY = fs.readFileSync(
  path.resolve(process.cwd(), "keys/jwt_private.pem"),
  "utf8"
);

const create_token = (id) => {
  const token = jwt.sign(
    { id },
    JWT_PRIVATE_KEY,
    {
      algorithm: "RS256",
      expiresIn: "1h",
    }
  );
  return { token }; 
};

export default create_token;