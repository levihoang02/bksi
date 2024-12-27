const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');

const Admin = sequelize.define('Admin', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
    },
    Aname: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    username: {
        type: DataTypes.STRING,
        unique: true,
        allowNull: false,
    },
    pwd: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: false,
    }
});

module.exports = Admin;