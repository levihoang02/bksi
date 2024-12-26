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
    }
});

module.exports = Service;