const { Kafka } = require('@confluentinc/kafka-javascript').KafkaJS;

const producer = new Kafka().producer({
    'bootstrap.servers': process.env.KAFKA_BROKERS_EXTERNAL,
});
let isConnected = false; // Track connection status

async function producerStart() {
    if (!isConnected) {
        await producer.connect();
        isConnected = true;
        console.log('Kafka producer connected');
    }
}

async function sendMessage(topic, message) {
    await producerStart(); // Ensure producer is connected
    await producer.send({
        topic,
        messages: [{ key: String(message.id), value: JSON.stringify(message) }],
    });

    console.log('Message sent:', message);
}

module.exports = { producer, sendMessage };
