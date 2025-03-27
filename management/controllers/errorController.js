const { logger } = require('../services/logger');

module.exports = (error, req, res, next) => {
    error.statusCode = error.statusCode || 500;
    error.status = error.status || 'error';

    // Log error with context
    logger.error('Application error', {
        statusCode: error.statusCode,
        message: error.message,
        stack: error.stack,
        path: req.originalUrl,
        method: req.method,
        requestId: req.id
    });

    res.status(error.statusCode).json({
        status: error.status,
        message: error.message,
        ...(process.env.NODE_ENV === 'development' && { stack: error.stack })
    });
};
