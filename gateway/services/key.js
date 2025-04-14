const { getClient, withRedisClient, setWithExpiry } = require('./redis');
const { hash } = require('../helpers/crypto');

const KEY_PREFIX = {
    API: 'api:keys',
};

function formatApiKey(key) {
    return `${KEY_PREFIX.API}:${key}`;
}

async function storeApiKey(hashKey, metadata = {}, expirySeconds = 24 * 3600) {
    // console.log('Storing...');

    await withRedisClient(async () => {
        const client = getClient();
        const formatHashKey = formatApiKey(hashKey);
        await client.hSet(formatHashKey, {
            created: Date.now().toString(),
            // ...metadata,
        });
        await client.expire(formatHashKey, expirySeconds);
    });
}

async function validateApiKey(apiKey) {
    const client = getClient();
    const hashKey = hash(apiKey);
    const data =
        (await withRedisClient(async () => {
            return await client.get(formatApiKey(hashKey));
        })) || {};

    // console.log(data);
    return Object.keys(data).length > 0 ? data : null;
}

module.exports = { storeApiKey, validateApiKey };
