const express = require('express');
const app = express();
const globalErrorHandler = require('./Controllers/errorController');
const helmet = require('helmet');
const cors = require('cors');
const routing = require('./routes/index');
const cookieParser = require('cookie-parser');

app.use(cors());

app.use(cookieParser());

app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(routing);

app.get('/', (req, res) => {
    res.send('Apis are ready!');
});

app.use(globalErrorHandler);

module.exports = app;