const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');
const Admin = require('./admin');

const Key = sequelize.define('Key', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV1,
        primaryKey: true,
    },
    value: {
        type: DataTypes.STRING,
        allowNull: false,
    },
    status: {
        type: DataTypes.ENUM('activated', 'expired'),
        allowNull: false,
        defaultValue: 'activated',
    },
    title: {
        type: DataTypes.STRING,
        allowNull: true,
    },
});

Admin.hasMany(Key);
Key.belongsTo(Admin);

module.exports = Key;
