const { getClient, withRedisClient } = require('./redis');
const axios = require('axios');

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

async function deleteServiceFromRedis(endPoint) {
    return withRedisClient(async () => {
        const client = getClient();
        const multi = client.multi();

        // Remove the sorted set for the given endpoint
        multi.del(`${endPoint}:connections`);

        const instanceKeys = await client.zRange(`${endPoint}:connections`, 0, -1);
        if (instanceKeys.length > 0) {
            // Delete each instance hash
            instanceKeys.forEach((instanceKey) => {
                multi.del(instanceKey); // Deleting the instance data from Redis
            });
        }

        return await multi.exec();
    });
}

async function deleteInstanceFromRedis(endPoint, instanceId) {
    return withRedisClient(async () => {
        const client = getClient();
        const multi = client.multi();

        const instanceKey = `${endPoint}:instances:${instanceId}`;

        multi.zRem(`${endPoint}:connections`, instanceKey);

        multi.del(instanceKey);

        return await multi.exec();
    });
}

async function updateAllInstancesStatus() {
    return withRedisClient(async () => {
        const client = getClient();
        const multi = client.multi();

        const allInstanceKeys = await client.keys('*:instances:*');

        if (allInstanceKeys.length === 0) {
            console.log('[CRON JOB] No instances found in Redis.');
            return;
        }

        for (const instanceKey of allInstanceKeys) {
            const instanceDetails = await client.hGetAll(instanceKey);
            const { host, port, status } = instanceDetails;

            // Perform health check by making a request to the /metrics endpoint
            const metricsUrl = `http://${host}:${port}/metrics`;
            let newStatus = status; // Default to current status if health check doesn't change

            try {
                const response = await axios.get(metricsUrl, { timeout: 10000 });

                // If the health check returns 200, mark as healthy (status 'true')
                if (response.status === 200) {
                    newStatus = 'true';
                    console.log(`${instanceKey} is healthy.`);
                } else {
                    newStatus = 'false';
                    console.log(`${instanceKey} is unhealthy (Status: ${response.status}).`);
                }
            } catch (error) {
                newStatus = 'false';
                console.log(`Failed to reach ${instanceKey} via /metrics: ${error.message}`);
            }

            // Update the status to 'true' or 'false' based on health check result
            multi.hSet(instanceKey, 'status', newStatus);
        }

        // Execute all multi commands at once (batching for efficiency)
        await multi.exec();
        console.log('Status updated for all instances in Redis.');
    });
}

module.exports = {
    storeInstances,
    incrementConnection,
    decrementConnection,
    getLeastConnectionsInstance,
    deleteInstanceFromRedis,
    deleteServiceFromRedis,
    updateAllInstancesStatus,
};
