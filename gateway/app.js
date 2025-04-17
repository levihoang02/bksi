const express = require('express');
const app = express();
const helmet = require('helmet');
const globalErrorHandler = require('./controllers/errorController');
const cors = require('cors');
const routing = require('./routes/index');
const cookieParser = require('cookie-parser');
const { requestLogger } = require('./services/logger');

const corsOptions = {
    origin: '*', // Allow all origins
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    credentials: true,
};

app.use(cors(corsOptions));
app.options('*', cors(corsOptions));

app.use(cookieParser());

app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(requestLogger);

app.use(routing);

app.get('/', (req, res) => {
    res.send('Apis are ready!');
});

app.use(globalErrorHandler);

module.exports = app;
