const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');
const ServiceRating = require('./serviceRating');
const Service = require('./service');

const RatingType = sequelize.define(
    'RatingType',
    {
        id: {
            type: DataTypes.SMALLINT,
            primaryKey: true,
            autoIncrement: true,
        },
        name: {
            type: DataTypes.STRING,
        },
    },
    {
        timestamps: false, // Disables `createdAt` and `updatedAt`
    },
);

ServiceRating.belongsToMany(RatingType, { through: ServiceRating });
RatingType.belongsToMany(Service, { through: ServiceRating });

// Service.hasMany(ServiceRating);
// ServiceRating.belongsTo(Service);

// RatingType.hasMany(ServiceRating);
// ServiceRating.belongsTo(RatingType);

module.exports = RatingType;
