const httpProxy = require('express-http-proxy');
const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');
const { findServiceInstanceByName } = require('../controllers/service.controller');
const {
    getLeastConnectionsInstance,
    incrementConnection,
    decrementConnection,
    storeInstances,
} = require('../services/loadbalancing');
require('dotenv').config();

const useService = asyncErrorHandler(async (req, res, next) => {
    const serviceName = req.body.service;
    let instanceKey;
    try {
        let serviceInstance = await getLeastConnectionsInstance(serviceName);
        //   console.log(serviceInstance);

        if (!serviceInstance) {
            // Fallback to fetching and storing service instances
            const serviceInstances = await findServiceInstanceByName(serviceName);
            if (serviceInstances && serviceInstances.length > 0) {
                await storeInstances(serviceName, serviceInstances);
                serviceInstance = serviceInstances[0]; // Pick the first one after storing
            }
        }

        if (!serviceInstance) {
            res.status(404).json({ message: 'Service is not available' });
            return;
        }
        instanceKey = `${serviceName}:instances:${serviceInstance.id}`;
        // Increment active connection count
        await incrementConnection(serviceName, instanceKey);

        // Construct the proxy path
        const path = `http://${serviceInstance.host}:${serviceInstance.port}${serviceInstance.endPoint || ''}`;
        console.log(`Proxying request to: ${path}`);

        // Proxy the request with enhanced error handling
        const proxyRequest = new Promise((resolve, reject) => {
            const proxyMiddleware = httpProxy(path, {
                proxyTimeout: 10000,
                timeout: 10000,
            });

            res.on('finish', () => {
                resolve();
            });

            proxyMiddleware(req, res, (proxyError) => {
                if (proxyError) {
                    console.error('Proxy error:', {
                        service: serviceName,
                        instance: instanceKey,
                        error: proxyError.message,
                        code: proxyError.code,
                    });
                    reject(proxyError);
                } else {
                    resolve();
                }
            });
        });

        await proxyRequest;

        console.log(instanceKey);
    } catch (err) {
        // console.error(`Error in useService: ${err.message}`);
        const error = new CustomError('Routing error', 500);
        next(error);
    } finally {
        // console.log(instanceKey);
        if (instanceKey) {
            await decrementConnection(serviceName, instanceKey);
        }
    }
});

module.exports = { useService };
