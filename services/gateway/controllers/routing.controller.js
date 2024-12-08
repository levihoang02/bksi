const httpProxy = require('express-http-proxy');
const asyncErrorHandler = require('../services/errorHandling');
const CustomError =  require('../utils/CustomError');
const {findServiceByName} = require('../controllers/service.controller');
require('dotenv').config();

const useSerivce = asyncErrorHandler(async (req, res, next) => {
      const id = req.body.id;
      const payload = req.body.payload;
      const serviceName = req.body.service;
      let endPoint;

      const service = await findServiceByName(serviceName);
      if(!service) {
          res.status(404).json({message: 'can not find service'});
          return;
      }

      if(!service.status) {
        res.status(404).json({message: 'service is not ready'});
        return;
      }

      if(service.endPoint) {
        endPoint = service.endPoint;
      }
      else {
        endPoint = "http://" + service.host + ":" + service.port;
      }
      console.log(endPoint);

      try {
        const serviceProxy = httpProxy(endPoint);
        serviceProxy(req, res, next);

      } catch(err) {
          const error = new CustomError(500);
          console.log(err);
          next(error);
      }
});


module.exports = {useSerivce};