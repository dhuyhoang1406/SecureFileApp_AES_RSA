'use strict';
const {
  Model
} = require('sequelize');
module.exports = (sequelize, DataTypes) => {
  class User extends Model {
    /**
     * Helper method for defining associations.
     * This method is not a part of Sequelize lifecycle.
     * The `models/index` file will call this method automatically.
     */
    static associate(models) {
      User.hasMany(models.File, { foreignKey: 'userId', as: 'files' });
    }
  }
  User.init({
    username: DataTypes.STRING,
    email: DataTypes.STRING,
    password: DataTypes.STRING,
    publicKey: DataTypes.TEXT,
    privateKey: DataTypes.TEXT
  }, {
    sequelize,
    modelName: 'User',
  });
  return User;
};