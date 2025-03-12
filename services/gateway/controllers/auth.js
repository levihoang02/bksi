const { createAPIToken, hash } = require('../helpers/crypto');
const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');
const { Key } = require('../models/index');

const generateAPIToken = asyncErrorHandler(async (req, res, next) => {
    try {
        const apiToken = createAPIToken();
        const hashToken = hash(apiToken, process.env.HASH_SECRET);
        const newKey = await Key.create({
            value: hashToken,
        });
        res.status(200).json({ status: 'success', token: apiToken });
    } catch (err) {
        const error = new CustomError('Internal Error', 500);
        next(error);
    }
});

module.exports = { generateAPIToken };
