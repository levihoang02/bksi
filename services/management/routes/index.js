const express = require('express');
const serviceController = require('../controllers/service.controller');
const ratingController = require('../controllers/rating.controller');

const router = require('express').Router();

/*CRUD service route */

router.get('/service', (req, res, next) => serviceController.getAllServiceInstances(req, res, next));

//create
router.post('/service', (req, res, next) => serviceController.createNewService(req, res, next));
//delete
router.delete('/service', (req, res, next) => serviceController.deleteService(req, res, next));
//update
router.put('/service', (req, res, next) => serviceController.updateService(req, res, next));

/*end CRUD service route */

/*instace service router */
router.post('/instance', (req, res, next) => serviceController.createServiceInstance(req, res, next));
router.delete('/instance', (req, res, next) => serviceController.deleteServiceInstance(req, res, next));
router.put('/instance', (req, res, next) => serviceController.updateServiceInstance(req, res, next));

/* rating route */

router.post('/rate', (req, res, next) => ratingController.createNewRating(req, res, next));

module.exports = router;
