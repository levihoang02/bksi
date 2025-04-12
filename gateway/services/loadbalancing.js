const { getClient, withRedisClient } = require('./redis');

async function storeInstances(endPoint, instances) {
    return withRedisClient(async () => {
        const client = getClient();
        const multi = client.multi();
        for (const instance of instances) {
            const instanceKey = `${endPoint}:instances:${instance.id}`;

            multi.hSet(
                instanceKey,
                'host',
                instance.host,
                // 'port', instance.port,
                // 'endpoint', instance.endpoint,
                // 'status', instance.status
            );

            multi.hSet(instanceKey, 'port', instance.port);

            multi.hSet(instanceKey, 'status', instance.status ? 'true' : 'false');

            // Add to sorted set with explicit parameters
            multi.zAdd(`${endPoint}:connections`, {
                score: 0,
                value: instanceKey,
            });
        }

        return await multi.exec();
    });
}

async function getLeastConnectionsInstance(endPoint) {
    return withRedisClient(async () => {
        const client = getClient();
        const connectionsKey = `${endPoint}:connections`;

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

async function incrementConnection(endPoint, instanceId) {
    return withRedisClient(async () => {
        const client = getClient();
        const connectionsKey = `${endPoint}:connections`;
        await client.zIncrBy(connectionsKey, 1, instanceId);
    });
}

async function decrementConnection(endPoint, instanceId) {
    // console.log("Decreasing...")
    return withRedisClient(async () => {
        const client = getClient();
        const connectionsKey = `${endPoint}:connections`;
        await client.zIncrBy(connectionsKey, -1, instanceId);
    });
}

module.exports = { storeInstances, incrementConnection, decrementConnection, getLeastConnectionsInstance };
