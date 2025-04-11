const express = require('express');
const routingController = require('../controllers/routing.controller');
const serviceController = require('../controllers/service.controller');
const authController = require('../controllers/auth');
const userController = require('../controllers/user.controller');
const { validateAPIKeyMiddleware, checkJwt } = require('../middlewares/auth');

const router = require('express').Router();

// user routes
router.post('/signup', userController.signup);
router.post('/login', userController.login);
router.post('logout', userController.logout);

router.get('/refresh', checkJwt, (req, res, next) => userController.refresh(req, res, next));
router.get('/key', checkJwt, (req, res, next) => authController.generateAPIToken(req, res, next));

// service route
router.post('/service', checkJwt, serviceController.createNewServiceAPI);
router.delete('/service', checkJwt, serviceController.deleteService);
router.get('/service', checkJwt, serviceController.getAllServiceAPI);
router.get('/service/:name', checkJwt, serviceController.getServiceByNameAPI);

router.post('/instance', checkJwt, serviceController.createNewInstanceAPI);
router.delete('/instance', checkJwt, serviceController.deleteInstanceAPI);

/*use service router */
// router.use(validateAPIKeyMiddleware);
router.post('/route/:endPoint/*', (req, res, next) => routingController.useService(req, res, next));
router.post('/route/:endPoint', (req, res, next) => routingController.useService(req, res, next));

router.get('/route/:endPoint/*', (req, res, next) => routingController.useService(req, res, next));
router.get('/route/:endPoint', (req, res, next) => routingController.useService(req, res, next));

router.delete('/route/:endPoint/*', (req, res, next) => routingController.useService(req, res, next));
router.delete('/route/:endPoint', (req, res, next) => routingController.useService(req, res, next));

router.put('/route/:endPoint/*', (req, res, next) => routingController.useService(req, res, next));
router.put('/route/:endPoint', (req, res, next) => routingController.useService(req, res, next));

router.patch('/route/:endPoint/*', (req, res, next) => routingController.useService(req, res, next));
router.patch('/route/:endPoint', (req, res, next) => routingController.useService(req, res, next));

module.exports = router;
