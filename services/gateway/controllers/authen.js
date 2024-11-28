const jwt = require('jsonwebtoken');
import asyncErrorHandler from '../services/errorHandling';

const generateAccessToken = (admin, secrectAccessToken, expiredTime) => {
    const token = jwt.sign(
        {
            id: admin.id,
            create: new Date(),
        },
        secrectAccessToken,
        {
            expiresIn: expiredTime,
        },
    );
    return token;
};

const generateRefreshToken = (admin, secrectRefreshToken, expiredTime) => {
    const token = jwt.sign(
        {
            id: admin.id,
            create: new Date(),
        },
        secrectRefreshToken,
        {
            expiresIn: expiredTime,
        },
    );

    return token;
};




module.exports = { generateAccessToken, generateRefreshToken };