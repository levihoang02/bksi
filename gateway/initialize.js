const config = require('./config')();
const serviceController = require('./controllers/service.controller');
const { storeInstances } = require('./services/loadbalancing');
const { initializeRedis } = require('./services/redis');
const { SeriveInsance } = require('./models');

const initialize = async () => {
    console.log('Inittialzing gateway...');
    await initializeRedis();
    let services = config.services;
    if (services) {
        for (const service of services) {
            let name = service['name'];
            let endPoint = service['endPoint'];
            let foundService = await serviceController.findServiceByEndPoint(endPoint);
            if (foundService) {
                let instances = await serviceController.findInstancesByServiceId(foundService.id);
                if (!instances) {
                    instances = service['instances'];
                    instances.forEach((instance) => {
                        instance['status'] = true;
                    });
                    instances.forEach((instance) => {
                        instance['ServiceId'] = foundService.id;
                    });
                    for (const i of instances) {
                        const exist = SeriveInsance.findOne({
                            where: {
                                id: i['id'],
                            },
                        });
                        if (!exist) {
                            await SeriveInsance.create(i);
                        }
                    }
                }
                instances = service['instances'];
                await storeInstances(endPoint, instances);
            } else {
                let instances = service['instances'];
                instances.forEach((instance) => {
                    instance['status'] = true;
                });
                await storeInstances(endPoint, instances);
                let newService = await serviceController.create(name, endPoint);
                instances.forEach((instance) => {
                    instance['ServiceId'] = newService.id;
                });
                await serviceController.createBulkInstances(instances);
            }
        }
    }
};

module.exports = initialize;
