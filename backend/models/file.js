"use strict";
import { Model } from "sequelize";

export default (sequelize, DataTypes) => {
  class File extends Model {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
    static associate(models) {
      File.belongsTo(models.User, { foreignKey: "userId", as: "user" });
    }
  }
  File.init(
    {
      filename: DataTypes.STRING,
      filePath: DataTypes.STRING,
      aesKey: DataTypes.TEXT,
      userId: DataTypes.INTEGER,
    },
    {
      sequelize,
      modelName: "File",
    }
  );
  return File;
};
