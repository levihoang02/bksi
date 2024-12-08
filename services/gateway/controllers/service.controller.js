const asyncErrorHandler = require('../services/errorHandling');
const CustomError =  require('../utils/CustomError');
const { Service } = require('../models');

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

const create = async (name, host=None, port=None, endPoint = None) => {
    
    const newService = await Service.create({
        Sname: name,
        host: host,
        port: port,
        endPoint: endPoint
    });

    return newService;
};

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

module.exports = {create, deleteService, findServiceById, findServiceByName};