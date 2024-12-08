const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');

const Service = sequelize.define('Service', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
    },
    Sname: {
        type: DataTypes.STRING,
        unique: true,
        allowNull: false,
    },
    host: {
        type: DataTypes.STRING,
        allowNull: true
    },
    port: {
        type: DataTypes.STRING,
        allowNull: true
    }, 
    endPoint: {
        type: DataTypes.STRING,
        allowNull: true
    },
    status: {
        type: DataTypes.BOOLEAN,
        allowNull: false,
        defaultValue: true
    }
});

module.exports = Service;