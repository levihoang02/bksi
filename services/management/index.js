const http = require('http');
const app = require('./app');
const dotenv = require('dotenv');
const sequelize = require('./services/database');
const initialize = require('./initialize');

sequelize.sync({ force: false }).then(() => {
    console.log('Database is ready');
    initialize().then(() => {
        console.log('Finish initalize Management');
        dotenv.config();

        const PORT = process.env.PORT || 3000;

        const sever = http.createServer(app);

        sever.listen(PORT, () => {
            console.log(`Service is running on port ${PORT}`);
        });
    });
});
