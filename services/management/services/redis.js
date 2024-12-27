const redis = require('redis');

const client = redis.createClient({
    host: '127.0.0.1',
    port: 6379,
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

process.on('SIGINT', async () => {
    try {
        await client.quit();
        console.log('Redis connection closed');
    } catch (error) {
        console.error('Error while closing Redis connection:', error);
    } finally {
        process.exit();
    }
});

module.exports = { client, withRedisClient };
