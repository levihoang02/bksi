const express = require('express');
const routingController = require('../controllers/routing.controller');
const serviceController = require('../controllers/service.controller');
const authController = require('../controllers/auth');
const { validateAPIKeyMiddleware } = require('../middlewares/auth');

const router = require('express').Router();

/*CRUD service route */

router.post('/services', (req, res, next) => routingController.useService(req, res, next));

//create
router.post('/service', (req, res, next) => routingController.useService(req, res, next));
//delete
router.delete('/service', (req, res, next) => routingController.useService(req, res, next));
//update
router.put('/service', (req, res, next) => routingController.useService(req, res, next));

/*end CRUD service route */

/*instace service router */
router.post('/instance', (req, res, next) => routingController.useService(req, res, next));
router.delete('/instance', (req, res, next) => routingController.useService(req, res, next));
router.put('/instance', (req, res, next) => routingController.useService(req, res, next));

/* rating route */

router.post('/rate', (req, res, next) => routingController.useService(req, res, next));

/*use service router */
router.post('/use', (req, res, next) => routingController.useService(req, res, next));

router.use(validateAPIKeyMiddleware);

router.post('/key', (req, res, next) => authController.generateAPIToken(req, res, next));

module.exports = router;
