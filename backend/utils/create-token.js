import jwt from "jsonwebtoken";
import crypto from "crypto";

const create_token = (id) => {
  const { privateKey: private_key_token, publicKey: public_key_token } =
    crypto.generateKeyPairSync("rsa", {
      modulusLength: 2048,
      publicKeyEncoding: { type: "pkcs1", format: "pem" },
      privateKeyEncoding: { type: "pkcs1", format: "pem" },
    });

  const token = jwt.sign({ id }, private_key_token, {
    algorithm: process.env.ALGORITHM_JWT || "RS256",
    expiresIn: process.env.EXPIRESIN_JWT || "1h",
  });

  return { token, public_key_token };
};

export default create_token;
