const { client, withRedisClient } = require('./redis');

async function storeInstances(serviceName, instances) {
    return withRedisClient(async () => {
        const multi = client.multi();

        for (const instance of instances) {
            const instanceKey = `${serviceName}:instances:${instance.id}`;

            multi.hSet(
                instanceKey,
                'host',
                instance.host,
                // 'port', instance.port,
                // 'endpoint', instance.endpoint,
                // 'status', instance.status
            );

            multi.hSet(instanceKey, 'port', instance.port);

            multi.hSet(instanceKey, 'endpoint', instance.endpoint || '');

            multi.hSet(instanceKey, 'status', instance.status ? 'true' : 'false');

            // Add to sorted set with explicit parameters
            multi.zAdd(`${serviceName}:connections`, {
                score: 0,
                value: instanceKey,
            });
        }

        return await multi.exec();
    });
}

async function getLeastConnectionsInstance(serviceName) {
    return withRedisClient(async () => {
        const connectionsKey = `${serviceName}:connections`;

        // Fetch all instances sorted by least connections
        const instanceKeys = await client.zRange(connectionsKey, 0, -1);
        // console.log(instanceKeys);

        if (!instanceKeys || instanceKeys.length === 0) {
            return null; // No instances available
        }

        for (const instanceKey of instanceKeys) {
            // Retrieve instance details from Redis
            const instanceDetails = await client.hGetAll(instanceKey);
            // console.log(instanceDetails);

            // Check if the instance is active
            if (instanceDetails.status === 'true') {
                return {
                    id: instanceKey.split(':').pop(), // Extract instance ID from the key
                    host: instanceDetails.host,
                    port: instanceDetails.port,
                    endpoint: instanceDetails.endpoint,
                };
            }
        }

        return null;
    });
}

async function incrementConnection(serviceName, instanceId) {
    return withRedisClient(async () => {
        const connectionsKey = `${serviceName}:connections`;
        await client.zIncrBy(connectionsKey, 1, instanceId);
    });
}

async function decrementConnection(serviceName, instanceId) {
    // console.log("Decreasing...")
    return withRedisClient(async () => {
        const connectionsKey = `${serviceName}:connections`;
        await client.zIncrBy(connectionsKey, -1, instanceId);
    });
}

module.exports = { storeInstances, incrementConnection, decrementConnection, getLeastConnectionsInstance };
