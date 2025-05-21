const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');
const { Service, ServiceInstance } = require('../models');
const sequelize = require('../services/database');
const { deleteInstanceFromRedis, deleteServiceFromRedis } = require('../services/loadbalancing');

require('dotenv').config();

const findServiceById = async (id) => {
    const service = Service.findOne({
        where: {
            id: id,
        },
    });
    return service;
};

const findServiceByName = async (name) => {
    const service = Service.findOne({
        where: {
            Sname: name,
        },
    });
    return service;
};

const findServiceByEndPoint = async (endPoint) => {
    const service = Service.findOne({
        where: {
            endPoint: endPoint,
        },
    });
    return service;
};

const findServiceInstanceEndPoint = async (endPoint) => {
    const serviceInstance = ServiceInstance.findAll({
        where: {
            status: true,
        },
        include: [
            {
                model: Service,
                where: {
                    endPoint: endPoint,
                },
            },
        ],
    });
    return serviceInstance;
};

const findInstancesByServiceId = async (serviceId) => {
    const instances = await ServiceInstance.findAll({
        where: {
            ServiceId: serviceId,
        },
    });
    return instances;
};

const create = async (name, endPoint) => {
    const newService = await Service.create({
        Sname: name,
        endPoint: endPoint,
    });

    return newService;
};

const createBulkInstances = async (instances) => {
    await ServiceInstance.bulkCreate(instances);
};

const deleteService = asyncErrorHandler(async (req, res, next) => {
    const name = req.params.name;
    try {
        const service = await Service.findOne({
            where: {
                Sname: name,
            },
        });
        await ServiceInstance.destroy({
            where: {
                serviceId: service.id,
            },
        });
        await Service.destroy({
            where: {
                Sname: name,
            },
        });
        await deleteServiceFromRedis(service.endPoint);
        res.status(200).json({ message: 'sucess' });
    } catch (err) {
        const error = new CustomError('failed to delete service', 500);
        next(error);
    }
});

const createNewServiceAPI = asyncErrorHandler(async (req, res, next) => {
    const name = req.body.name;
    const endPoint = req.body.endPoint;
    const instances = req.body.instances;
    const t = await sequelize.transaction();
    try {
        const newService = await Service.create(
            {
                Sname: name,
                endPoint: endPoint,
            },
            { transaction: t },
        );
        instances.forEach((instance, index) => {
            instance['status'] = true;
            instance['ServiceId'] = newService.id;
            instance['id'] = `${name}${index}`;
        });
        await ServiceInstance.bulkCreate(instances, { transaction: t });
        await t.commit();
        res.status(200).json({ message: 'sucess' });
    } catch (err) {
        await t.rollback();
        const error = new CustomError(`Failed to add services: ${err.message}`, 500);
        console.log(err);
        next(error);
    }
});

const createNewInstanceAPI = asyncErrorHandler(async (req, res, next) => {
    const id = req.body.id;
    const host = req.body.host;
    const port = req.body.port;
    try {
        const instances = await ServiceInstance.findAll({
            where: {
                ServiceId: id,
            },
        });
        const service = await Service.findOne({
            attributes: ['Sname'],
            where: {
                id: id,
            },
        });
        await ServiceInstance.create({
            id: `${service.Sname}${instances.length}`,
            host: host,
            port: port,
            ServiceId: id,
        });
        res.status(200).json({ message: 'sucess' });
    } catch (err) {
        const error = new CustomError(`Failed to add instance: ${err.message}`, 500);
        next(error);
    }
});

const deleteInstanceAPI = asyncErrorHandler(async (req, res, next) => {
    const id = req.params.id;
    try {
        const instance = await ServiceInstance.findOne({
            where: {
                id: id,
            },
        });
        const service = await Service.findOne({
            where: {
                id: instance.ServiceId,
            },
        });
        await ServiceInstance.destroy({
            where: {
                id: id,
            },
        });
        await deleteInstanceFromRedis(service.endPoint, instance.id);
        res.status(200).json({ message: 'success' });
    } catch (err) {
        const error = new CustomError(`Failed to delete instance, ${err.message}`, 500);
        next(error);
    }
});

const getAllServiceAPI = asyncErrorHandler(async (req, res, next) => {
    try {
        const result = await Service.findAll({
            attributes: ['id', 'Sname', 'endPoint'],
            include: [
                {
                    model: ServiceInstance,
                    attributes: ['id', 'host', 'port'],
                },
            ],
        });

        res.status(200).json({ message: 'success', data: result });
    } catch (err) {
        const error = new CustomError(`Failed to get all service, ${err.message}`, 500);
        next(error);
    }
});

const getServiceByNameAPI = asyncErrorHandler(async (req, res, next) => {
    const name = req.params.name;
    try {
        const result = await Service.findOne({
            attributes: ['id', 'Sname', 'endPoint'],
            where: {
                Sname: name,
            },
            include: [
                {
                    model: ServiceInstance,
                    attributes: ['host', 'port'],
                },
            ],
        });

        res.status(200).json({ message: 'success', data: result });
    } catch (err) {
        const error = new CustomError(`Failed to get service, ${err.message}`, 500);
        next(error);
    }
});

module.exports = {
    create,
    deleteService,
    findServiceByEndPoint,
    findServiceInstanceEndPoint,
    createBulkInstances,
    findInstancesByServiceId,
    findServiceByName,
    findServiceById,
    createNewServiceAPI,
    deleteInstanceAPI,
    createNewInstanceAPI,
    getAllServiceAPI,
    getServiceByNameAPI,
};
