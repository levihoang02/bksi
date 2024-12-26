const config= require ('./config')();
const serviceController = require('./controllers/service.controller');
const {storeInstances} = require('./services/loadbalancing');

const initialize = async() => {
    console.log("Inittialzing gateway...")
    let services = config.services;
    if(services) {
        for(const service of services) {
            let name = service["name"];
            let foundService = await serviceController.findServiceByName(name);
            if(foundService) {
                let instances = await serviceController.findInstancesByServiceId(foundService.id);
                await storeInstances(name, instances);
            }
            else {
                let instances = service["instances"];
                instances.forEach(instance => {
                    instance["status"] = "ACTIVE";
                });
                await storeInstances(name, instances);
                let newService = await serviceController.create(name, instances);
                instances.forEach(instance => {
                    instance["ServiceId"] = newService.id;
                });
                await serviceController.createBulkInstances(instances);
            }
        };
    }
};

module.exports = initialize;