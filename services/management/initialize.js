const serviceController = require('./controllers/service.controller');
const { storeInstances } = require('./services/loadbalancing');

const initialize = async () => {
    console.log('Inittialzing managmenet...');
};

module.exports = initialize;
