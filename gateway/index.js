const http = require('http');
const app = require('./app');
const cron = require('node-cron');
// const dotenv = require('dotenv');
// dotenv.config();
const sequelize = require('./services/database');
const config = require('./config')();
const initialize = require('./initialize');
const { updateAllInstancesStatus } = require('./services/loadbalancing');

const updateServiceStatusCronJob = () => {
    cron.schedule('*/1 * * * *', async () => {
        console.log('Running service status update for all instances...');
        await updateAllInstancesStatus();
    });
};

sequelize.sync({ force: false }).then(() => {
    console.log('Database is ready');
    initialize().then(() => {
        console.log('Finish initalize gateway');

        const PORT = config.gateway.port || 3000;

        const sever = http.createServer(app);

        sever.listen(PORT, () => {
            console.log(`Server is running on port ${PORT}`);
        });
        updateServiceStatusCronJob();
    });
});
