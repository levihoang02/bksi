const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');
const { Service, ServiceInstance } = require('../models');

require('dotenv').config();

const getAllServiceInstances = asyncErrorHandler(async (req, res, next) => {
    try {
        const result = await Service.findAll({
            include: [
                {
                    model: ServiceInstance,
                },
            ],
        });
        res.status(200).json({ message: 'success', data: result });
    } catch (err) {
        const error = new CustomError('Failed to fetech services', 500);
        next(error);
    }
});

/* Service controllers */

const createNewService = asyncErrorHandler(async (req, res, next) => {
    const name = req.body.name;
    try {
        const newService = await Service.create({
            Sname: name,
        });

        res.status(200).json({ message: 'success', data: newService.id });
    } catch (err) {
        const error = new CustomError('Can not create new service', 500);
        next(error);
    }
});

const updateService = asyncErrorHandler(async (req, res, next) => {
    const id = req.body.id;
    const newName = req.body.name;
    try {
        const service = await Service.update({
            Sname: newName,
        });
        res.status(200).json({ message: 'success', data: service });
    } catch (err) {
        const error = new CustomError('Failed to update service', 500);
        next(error);
    }
});

const deleteService = asyncErrorHandler(async (req, res, next) => {
    const id = req.body.id;
    const transaction = await sequelize.transaction();
    try {
        await ServiceInstance.destroy(
            {
                where: {
                    ServiceId: id,
                },
            },
            transaction,
        );

        await Service.destroy(
            {
                where: {
                    id: id,
                },
            },
            transaction,
        );

        await transaction.commit();
        res.status(200).json({ message: 'success' });
    } catch (err) {
        await transaction.rollback();
        const error = new CustomError('Failed to delete service', 500);
        next(error);
    }
});

/* Service instance controllers */

const createServiceInstance = asyncErrorHandler(async (req, res, next) => {
    const id = req.body.id;
    const host = req.body.host;
    const port = req.body.port;
    const endPoint = req.body.endPoint || '';
    const serviceName = req.body.name;

    try {
        const service = await Service.findOne({
            where: {
                Sname: serviceName,
            },
        });

        if (!service) {
            try {
                const transaction = await sequelize.transaction();
                const newService = await Service.create(
                    {
                        Sname: serviceName,
                    },
                    { transaction },
                );

                const newInstance = await ServiceInstance.create(
                    {
                        id: id,
                        host: host,
                        port: port,
                        endPoint: endPoint,
                        ServiceId: newService.id,
                    },
                    { transaction },
                );

                await transaction.commit();
                return res
                    .staus(200)
                    .json({ message: 'success', data: { service: newService, instance: newInstance } });
            } catch (err) {
                const error = new CustomError('Failed to create new instance', 500);
                await transaction.rollback();
                return next(error);
            }
        } else {
            const newInstance = await ServiceInstance.create({
                id: id,
                host: host,
                port: port,
                endPoint: endPoint,
                ServiceId: newService.id,
            });
            return res.staus(200).json({ message: 'success', data: { service: service, instance: newInstance } });
        }
    } catch (err) {
        const error = new CustomError('Failed to create new instance', 500);
        return next(error);
    }
});

const updateServiceInstance = asyncErrorHandler(async (req, res, next) => {
    const id = req.body.id;
    const host = req.body.host;
    const port = req.body.port;
    const endPoint = req.body.endpoint;
    try {
        const instance = await ServiceInstance.update({
            id: id,
            host: host,
            port: port,
            endPoint: endPoint,
        });

        res.status(200).json({ message: 'success', data: instance });
    } catch (err) {
        const error = new CustomError('Failed to update service instance', 500);
        next(error);
    }
});

const deleteServiceInstance = asyncErrorHandler(async (req, res, next) => {
    const id = req.body.id;
    try {
        await ServiceInstance.destroy({
            where: {
                id: id,
            },
        });
        res.status(200).json({ message: 'success' });
    } catch (err) {
        const error = new CustomError('Failed to delete instance', 500);
        next(error);
    }
});

module.exports = {
    createNewService,
    updateService,
    deleteService,
    createServiceInstance,
    updateServiceInstance,
    deleteServiceInstance,
};
