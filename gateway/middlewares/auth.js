const { validateToken } = require('../helpers/crypto');
const asyncErrorHandler = require('../services/errorHandling');
const { Key } = require('../models/index');
const CustomError = require('../utils/CustomError');
const { validateApiKey, storeApiKey } = require('../services/key');
const { hash } = require('../helpers/crypto');

const validateAPIKeyMiddleware = asyncErrorHandler(async (req, res, next) => {
    try {
        const apiKey = req.headers['bksi-api-key'];
        if (!apiKey) {
            return res.status(401).json({ message: 'Forbidden' });
        }
        const redisData = await validateApiKey(apiKey);
        if (redisData) {
            return next();
        }

        const hashKey = hash(apiKey);
        const key = await Key.findOne({
            where: {
                value: hashKey,
            },
        });

        if (!key) {
            return res.status(401).json({ message: 'Forbidden' });
        }

        await storeApiKey(hashKey, key);
        next();
    } catch (err) {
        console.log(err);
        const error = new CustomError('Authentication Error', 500);
        next(error);
    }
});

module.exports = { validateAPIKeyMiddleware };
