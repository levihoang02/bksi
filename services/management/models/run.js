const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');
const ServiceInstance = require('./serviceInstance');

const Run = sequelize.define('Run', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
    },
    status: {
        type: DataTypes.BOOLEAN,
    },
});

ServiceInstance.hasMany(Run);
Run.belongsTo(ServiceInstance);

module.exports = Run;
