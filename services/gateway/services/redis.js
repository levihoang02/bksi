const redis = require('redis');

const client = redis.createClient({
    host: '127.0.0.1',
    port: 6379  
});

async function withRedisClient(operation) {
    if (!client.isOpen) {
        await client.connect();
    }
    try {
        return await operation();
    } catch (error) {
        console.error('Redis operation failed:', error);
        throw error;
    }
}

module.exports = { client, withRedisClient };