const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');
const Service = require('./service');

const ServiceRating = sequelize.define('ServiceInstance', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
    },
});

Service.hasMany(ServiceRating);
ServiceRating.belongsTo(Service);

module.exports = ServiceRating;
