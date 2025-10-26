"use strict";

import fs from "fs";
import path from "path";
import { fileURLToPath, pathToFileURL } from "url";
import Sequelize from "sequelize";
import configObj from "../config/config.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const basename = path.basename(__filename);
const env = process.env.NODE_ENV || "development";
const config = configObj[env];

const db = {};

let sequelize;
if (config.use_env_variable) {
  sequelize = new Sequelize(process.env[config.use_env_variable], config);
} else {
  sequelize = new Sequelize(
    config.database,
    config.username,
    config.password,
    config
  );
}

const files = fs.readdirSync(__dirname).filter((file) => {
  return (
    file.indexOf(".") !== 0 &&
    file !== basename &&
    file.slice(-3) === ".js" &&
    file.indexOf(".test.js") === -1
  );
});

for (const file of files) {
  const filePath = path.join(__dirname, file);
  const fileUrl = pathToFileURL(filePath).href;
  const imported = await import(fileUrl);
  const modelDef = imported.default;
  if (typeof modelDef === "function") {
    const model = modelDef(sequelize, Sequelize.DataTypes);
    db[model.name] = model;
  }
}

Object.keys(db).forEach((modelName) => {
  if (db[modelName].associate) {
    db[modelName].associate(db);
  }
});

db.sequelize = sequelize;
db.Sequelize = Sequelize;

const User = db.User;
const File = db.File;

export default db;
export { User, File };
