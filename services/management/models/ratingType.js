const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');
const ServiceRating = require('./serviceRating');
const Service = require('./service');

const RatingType = sequelize.define('ServiceInstance', {
    id: {
        type: DataTypes.SMALLINT,
        primaryKey: true,
        autoIncrement: true,
    },
    name: {
        type: DataTypes.STRING,
    },
});

ServiceRating.belongsToMany(RatingType, { through: { model: RatingType, as: 'Owned', unique: false } });
RatingType.belongsToMany(Service, { through: { model: RatingType, as: 'Owned', unique: false } });

Service.hasMany(ServiceRating);
ServiceRating.belongsTo(Service);

RatingType.hasMany(ServiceRating);
ServiceRating.belongsTo(RatingType);

module.exports = RatingType;
