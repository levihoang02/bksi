const express = require('express');
const app = express();
const globalErrorHandler = require('./controllers/errorController');
const routing = require('./routes/index');
const cookieParser = require('cookie-parser');
const { requestLogger } = require('./services/logger');

app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(requestLogger);

app.use(routing);

app.get('/', (req, res) => {
    res.send('Apis are ready!');
});

app.use(globalErrorHandler);

module.exports = app;
