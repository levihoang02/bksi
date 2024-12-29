const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');

const { ServiceRating, Service } = require('../models');

const createNewRating = asyncErrorHandler(async (req, res, next) => {
    const serviceName = req.body.serviceName;
    const ratingType = req.body.type;

    try {
        const service = await Service.findOne({
            where: {
                Sname: serviceName,
            },
        });
        if (!service) {
            return res.status(404).json({ message: 'Service not found' });
        }
        await ServiceRating.create({
            RatingTypeId: ratingType,
            ServiceId: service.id,
        });
        res.status(200).json({ message: 'success' });
    } catch (err) {
        const error = new CustomError('Failed to rate service', 500);
        next(error);
    }
});

module.exports = { createNewRating };
