const config= require ('./config')();
const serviceController = require('./controllers/service.controller');

const initialize = async() => {
    console.log("Inittialzing gateway...")
    let services = config.services;
    if(services) {
        for(let i=0; i<services.length; i++) {
            let service = services[i];
            if(await serviceController.findServiceByName(service.name)) continue;
            await serviceController.create(service.name, service.host, service.port, service.endPoint);
        }
    }
};

module.exports = initialize;