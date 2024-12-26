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
        type: DataTypes.STRING,
        allowNull: false,
        defaultValue: "ACTIVE"
    }
});

Service.hasMany(ServiceInstance);
ServiceInstance.belongsTo(Service);

module.exports = ServiceInstance;