const asyncErrorHandler = require('../services/errorHandling');
const CustomError =  require('../utils/CustomError');
const { Service, ServiceInstance } = require('../models');

require('dotenv').config();

const findServiceById = async (id) => {
    const service = Service.findOne({
        where: {
            id: id
        }
    })
    return service;
};

const findServiceByName = async (name) => {
    const service = Service.findOne({
        where: {
            Sname: name
        }
    })
    return service;
};

const findInstancesByServiceId = async(serviceId) => {
    const instances = await ServiceInstance.findAll({
        where: {
            ServiceId: serviceId
        }
    })
    return instances;
}


const create = async (name) => {
    
    const newService = await Service.create({
        Sname: name,
    });

    return newService;
};

const createBulkInstances = async (instances) => {
    await ServiceInstance.bulkCreate(instances);
}

const deleteService = asyncErrorHandler(async(req, res, next) => {
    const id = req.body.id;
    try {
        await Service.destroy({
            where: {
                id: id
            }
        });
        res.status(200).json({message: 'sucess'});
    } catch(err) {
        const error = new CustomError('failed to delete service', 500);
        next(error);
    }
});

module.exports = {create, deleteService, findServiceById, findServiceByName, createBulkInstances, findInstancesByServiceId };