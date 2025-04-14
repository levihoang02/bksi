const httpProxy = require('express-http-proxy');
const CircuitBreaker = require('opossum');
const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');
const { findServiceInstanceEndPoint } = require('../controllers/service.controller');
const {
    getLeastConnectionsInstance,
    incrementConnection,
    decrementConnection,
    storeInstances,
} = require('../services/loadbalancing');
require('dotenv').config();

async function proxyServiceRequest(req, res, serviceInstance, endPoint, instanceKey, proxyEndpoint) {
    return new Promise((resolve, reject) => {
        let path = `http://${serviceInstance.host}:${serviceInstance.port}`;
        if (proxyEndpoint) {
            path = `${path}/${proxyEndpoint.replace(/^\/+|\/+$/g, '')}`;
        }

        const proxyMiddleware = httpProxy(path, {
            proxyTimeout: 10000,
            timeout: 10000,
            proxyReqPathResolver: function (req) {
                const originalPath = req.url;
                const newPath = originalPath.replace(`/route/${endPoint}`, '');
                return newPath || '/';
            },
        });

        res.on('finish', () => {
            resolve();
        });

        proxyMiddleware(req, res, (proxyError) => {
            if (proxyError) {
                console.error('Proxy error:', {
                    service: endPoint,
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
}

const breakerOptions = {
    timeout: 30000,
    errorThresholdPercentage: 50, // % of failures before opening the circuit
    resetTimeout: 30000,
};

const proxyBreaker = new CircuitBreaker(proxyServiceRequest, breakerOptions);

// Fallback if service is unavailable
proxyBreaker.fallback(() => {
    throw new CustomError('Circuit breaker: service temporarily unavailable', 503);
});

const useService = asyncErrorHandler(async (req, res, next) => {
    const endPoint = req.params.endPoint;
    const proxyEndpoint = req.params[0];
    let instanceKey;
    try {
        let serviceInstance = await getLeastConnectionsInstance(endPoint);
        //   console.log(serviceInstance);
        if (!serviceInstance) {
            // Fallback to fetching and storing service instances
            const serviceInstances = await findServiceInstanceEndPoint(endPoint);
            if (serviceInstances && serviceInstances.length > 0) {
                const plainInstances = serviceInstances.map((instance) => instance.get({ plain: true }));
                await storeInstances(endPoint, plainInstances);
                serviceInstance = serviceInstances[0]; // Pick the first one after storing
            }
        }
        if (!serviceInstance) {
            res.status(404).json({ message: 'Service is not available' });
            return;
        }
        instanceKey = `${endPoint}:instances:${serviceInstance.id}`;
        // Increment active connection count
        await incrementConnection(endPoint, instanceKey);

        // // Construct the proxy path
        // let path = `http://${serviceInstance.host}:${serviceInstance.port}`;
        // if (proxyEndpoint) {
        //     path = `${path}/${proxyEndpoint.replace(/^\/+|\/+$/g, '')}`;
        // }
        // console.log(`Proxying request to: ${path}`);

        // Proxy the request
        // const proxyRequest = new Promise((resolve, reject) => {
        //     const proxyMiddleware = httpProxy(path, {
        //         proxyTimeout: 10000,
        //         timeout: 10000,
        //         proxyReqPathResolver: function (req) {
        //             const originalPath = req.url;
        //             const newPath = originalPath.replace(`/route/${endPoint}`, '');
        //             return newPath || '/';
        //         },
        //     });

        //     res.on('finish', () => {
        //         resolve();
        //     });

        //     proxyMiddleware(req, res, (proxyError) => {
        //         if (proxyError) {
        //             console.error('Proxy error:', {
        //                 service: endPoint,
        //                 instance: instanceKey,
        //                 error: proxyError.message,
        //                 code: proxyError.code,
        //             });
        //             reject(proxyError);
        //         } else {
        //             resolve();
        //         }
        //     });
        // });

        // await proxyRequest;
        await proxyBreaker.fire(req, res, serviceInstance, endPoint, instanceKey, proxyEndpoint);

        // console.log(instanceKey);
    } catch (err) {
        // console.error(`Error in useService: ${err.message}`);
        next(err instanceof CustomError ? err : new CustomError(`Routing error ${err.message}`, 500));
    } finally {
        // console.log(instanceKey);
        if (instanceKey) {
            await decrementConnection(endPoint, instanceKey);
        }
    }
});

module.exports = { useService };
