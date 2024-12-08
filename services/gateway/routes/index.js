const express = require('express');
const routingController = require('../controllers/routing.controller');
const serviceController = require('../controllers/service.controller');

const router = require('express').Router();

/*CRUD service route */

//create
router.post('/service', (req, res, next) => serviceController.create(req, res, next));
//delete
router.delete('/services', (req, res, next)=> serviceController.deleteService(req, res, next));

/*end CRUD service route */


/*use service router */
router.post('/use', (req, res, next) => routingController.useSerivce(req, res, next));

module.exports = router;