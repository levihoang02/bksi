const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');
const Service = require('./service');

const ServiceInstance = sequelize.define('ServiceInstance', {
    id: {
        type: DataTypes.STRING,
        primaryKey: true,
    },
    host: {
        type: DataTypes.STRING,
        allowNull: true,
    },
    port: {
        type: DataTypes.STRING,
        allowNull: true,
    },
    status: {
        type: DataTypes.BOOLEAN,
        allowNull: false,
        defaultValue: true,
    },
});

Service.hasMany(ServiceInstance);
ServiceInstance.belongsTo(Service);

module.exports = ServiceInstance;
