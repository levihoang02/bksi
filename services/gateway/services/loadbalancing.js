const { client, withRedisClient } = require("./redis");

async function storeInstances(serviceName, instances) {
    return withRedisClient(async () => {
        const multi = client.multi();

        for (const instance of instances) {
            const instanceKey = `${serviceName}:instances:${instance.id}`;
            
            multi.hSet(
                instanceKey,
                'host', instance.host,
                // 'port', instance.port,
                // 'endpoint', instance.endpoint,
                // 'status', instance.status
            );

            multi.hSet(
                instanceKey,
                'port', instance.port,
            )

            if(instance.endPoint) {
                multi.hSet(
                    instanceKey,
                    'endpoint', instance.endpoint,
                )
            }

            multi.hSet(
                instanceKey, 
                'status', instance.status
            )

            // Add to sorted set with explicit parameters
            multi.zAdd(
                `${serviceName}:connections`,
                {
                    score: 0,
                    value: instanceKey
                }
            );
        }

        return await multi.exec();
    });
}

async function getLeastConnectionsInstance(serviceName) {
    return withRedisClient(async () => {
        const connectionsKey = `${serviceName}:connections`;

        const [instanceKey] = await client.zRange(connectionsKey, 0, 0);

        if (!instanceKey) {
            throw new Error('No active instances available');
        }

        const instanceDetails = await client.hGetAll(instanceKey);

        return {
            id: instanceKey,
            host: instanceDetails.host,
            port: instanceDetails.port,
            endpoint: instanceDetails.endpoint,
        };
    });
}

async function incrementConnection(serviceName, instanceId) {
    return withRedisClient(async () => {
        const connectionsKey = `${serviceName}:connections`;
        await client.zIncrBy(connectionsKey, 1, instanceId);
    });
}

async function decrementConnection(serviceName, instanceId) {
    return withRedisClient(async () => {
        const connectionsKey = `${serviceName}:connections`;
        await client.zIncrBy(connectionsKey, -1, instanceId);
    });
}

module.exports = { storeInstances, incrementConnection, decrementConnection, getLeastConnectionsInstance };