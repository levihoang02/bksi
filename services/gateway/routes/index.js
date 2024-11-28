const express = require('express');
const routingController = require('../controllers/routing');

const router = require('express').Router();

router.post('/highlight', (req, res, next) => routingController.highlightRouting(req, res, next))

module.exports = router;