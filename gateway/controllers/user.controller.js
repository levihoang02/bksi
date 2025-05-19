const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { Admin } = require('../models');
const asyncErrorHandler = require('../services/errorHandling');
const CustomError = require('../utils/CustomError');

const ACCESS_SECRET = process.env.JWT_SECRET;
const REFRESH_SECRET = process.env.JWT_REFRESH_SECRET;
const ACCESS_EXP = process.env.ACCESS_TOKEN_EXP || '15m';
const REFRESH_EXP = process.env.REFRESH_TOKEN_EXP || '7d';

const createTokens = (admin) => {
    const accessToken = jwt.sign({ adminId: admin.id, username: admin.username }, ACCESS_SECRET, {
        expiresIn: ACCESS_EXP,
    });

    const refreshToken = jwt.sign({ adminId: admin.id }, REFRESH_SECRET, { expiresIn: REFRESH_EXP });

    return { accessToken, refreshToken };
};

const signup = asyncErrorHandler(async (req, res, next) => {
    const Aname = req.body.Aname;
    const username = req.body.username;
    const password = req.body.password;

    const existingAdmin = await Admin.findOne({ where: { username: username } });
    if (existingAdmin) {
        return res.status(400).json({ message: 'Username already exists' });
    }
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    const newAdmin = await Admin.create({
        Aname: Aname,
        username: username,
        pwd: hashedPassword,
    });
    res.status(201).json({
        message: 'Admin created successfully',
        adminId: newAdmin.id,
    });
});

const login = asyncErrorHandler(async (req, res, next) => {
    const username = req.body.username;
    const password = req.body.password;

    const admin = await Admin.findOne({ where: { username } });
    if (!admin) return res.status(404).json({ message: 'Admin not found' });

    const match = await bcrypt.compare(password, admin.pwd);
    if (!match) return res.status(401).json({ message: 'Invalid credentials' });

    const { accessToken, refreshToken } = createTokens(admin);

    // Set cookies (secure, HTTP-only)
    res.cookie('accessToken', accessToken, { httpOnly: true, sameSite: 'strict', maxAge: 15 * 60 * 1000 })
        .cookie('refreshToken', refreshToken, { httpOnly: true, sameSite: 'strict', maxAge: 7 * 24 * 60 * 60 * 1000 })
        .status(200)
        .json({ message: 'Login successful', id: admin.id });
});

const refresh = asyncErrorHandler(async (req, res) => {
    const token = req.cookies.refreshToken;
    if (!token) return res.status(401).json({ message: 'No refresh token' });

    try {
        const decoded = jwt.verify(token, REFRESH_SECRET);
        const admin = await Admin.findByPk(decoded.adminId);
        if (!admin) return res.status(401).json({ message: 'Invalid refresh token' });

        const { accessToken, refreshToken } = createTokens(admin);

        res.cookie('accessToken', accessToken, {
            httpOnly: true,
            secure: true,
            sameSite: 'none',
            maxAge: 15 * 60 * 1000,
        })
            .cookie('refreshToken', refreshToken, {
                httpOnly: true,
                secure: true,
                sameSite: 'none',
                maxAge: 7 * 24 * 60 * 60 * 1000,
            })
            .status(200)
            .json({ message: 'Tokens refreshed' });
    } catch (err) {
        return res.status(403).json({ message: 'Token expired or invalid' });
    }
});

const logout = asyncErrorHandler(async (req, res, next) => {
    res.clearCookie('accessToken', {
        httpOnly: true,
        secure: true,
        sameSite: 'none',
        path: '/',
    }).clearCookie('refreshToken', {
        httpOnly: true,
        secure: true,
        sameSite: 'none',
        path: '/',
    });
    res.status(200).json({ message: 'Logout successful. Please clear your token on client.' });
});

module.exports = { login, logout, signup, refresh };
