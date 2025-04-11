const redis = require('redis');

let client = null;
let redisAvailable = false;
const RECONNECT_INTERVAL = 30000;

function setupRedisClient() {
    if (client) {
        // Clean up existing listeners and client
        client.removeAllListeners();
        client.quit().catch(() => {});
    }

    client = redis.createClient({
        host: '127.0.0.1',
        port: 6379,
        retry_strategy: () => null,
    });

    client.on('error', () => {
        redisAvailable = false;
        client.removeAllListeners();
        client.quit().catch(() => {});
        client = null;
    });

    client.on('end', () => {
        redisAvailable = false;
        client.removeAllListeners();
        client.quit().catch(() => {});
        client = null;
    });

    client.on('connect', () => {
        console.log('Redis connected');
        redisAvailable = true;
    });

    return client;
}

async function tryConnect() {
    try {
        if (!client) {
            client = setupRedisClient();
            console.log(client);
        }
        if (client && !client.isOpen) {
            await Promise.race([
                client.connect(),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Connection timeout')), 5000)),
            ]);
        }
        return true;
    } catch (error) {
        redisAvailable = false;
        return false;
    }
}

// Initial connection attempt
setupRedisClient();

async function initializeRedis() {
    console.log('Initializing Redis...');
    try {
        const connected = await tryConnect();
        if (!connected) {
            throw new Error('Failed to connect to Redis');
        }
        console.log('Redis initialization complete');
        return true;
    } catch (error) {
        console.error('Redis initialization failed:', error);
        throw error;
    }
}

async function withRedisClient(operation) {
    if (!redisAvailable || !client) {
        await tryConnect();
    }

    try {
        return await operation();
    } catch (error) {
        console.warn('Redis operation failed:', error.message);
        redisAvailable = false; // Mark as unavailable on error
        return null;
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

async function setWithExpiry(key, value, expirySeconds = 3600) {
    return await withRedisClient(async () => {
        // Using built-in SET with EX option
        await client.set(key, value, { EX: expirySeconds });
    });
}

module.exports = { client, withRedisClient, setWithExpiry, initializeRedis };
