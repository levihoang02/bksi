const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');
const { Service, ServiceInstance } = require('../models');
const { sendMessage } = require('../services/kafka');

require('dotenv').config();

const generateInstanceName = (serviceName) => {
    return `${serviceName}-${Date.now()}`;
};

const generateId = () => {
    return Math.floor((Date.now() % 10000000000) * Math.random());
};

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

const findServiceInstanceByName = async (name) => {
    const serviceInstance = ServiceInstance.findOne({
        where: {
            status: true,
        },
        include: [
            {
                model: Service,
                where: {
                    Sname: name,
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

const create = async (name) => {
    const newService = await Service.create({
        Sname: name,
    });

    return newService;
};

const createBulkInstances = async (instances) => {
    await ServiceInstance.bulkCreate(instances);
};

const createNewServiceInstance = asyncErrorHandler(async (req, res, next) => {
    const name = req.body.name;
    const host = req.body.host;
    const port = req.body.port;
    const endPoint = req.body.endPoint || null;

    try {
        const [service, created] = await Service.findOrCreate({
            where: {
                Sname: name,
            },
        });

        const instanceName = generateInstanceName(name);
        const newInstance = await ServiceInstance.create({
            id: instanceName,
            host: host,
            port: port,
            endPoint: endPoint,
            status: true,
            serviceId: service.id,
        });

        const payload = {
            name: instanceName,
            host: host,
            port: port,
        };

        let event = {
            id: generateId(),
            source: 'gateway',
            type: 'CREATED_NEW_SERVICE',
            payload: payload,
        };

        sendMessage('dashboard', event);
        res.status(200).json({ message: 'success' });
    } catch (err) {
        console.log(err);
        const error = new CustomError('Create service error', 500);
        next(error);
    } finally {
        await producer.disconnect();
    }
});

const deleteService = asyncErrorHandler(async (req, res, next) => {
    const id = req.body.id;
    try {
        await Service.destroy({
            where: {
                id: id,
            },
        });
        res.status(200).json({ message: 'sucess' });
    } catch (err) {
        const error = new CustomError('failed to delete service', 500);
        next(error);
    }
});

module.exports = {
    create,
    deleteService,
    findServiceById,
    findServiceInstanceByName,
    createBulkInstances,
    findInstancesByServiceId,
    findServiceByName,
    createNewServiceInstance,
};
