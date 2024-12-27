const { DataTypes } = require('sequelize');
const sequelize = require('../services/database');
const ServiceRating = require('./serviceRating');

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

ServiceRating.hasOne(RatingType);
RatingType.belongsToMany(ServiceRating);

module.exports = RatingType;
