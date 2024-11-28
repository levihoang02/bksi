const asyncErrorHandler = require('../services/errorHandling');
const CustomError =  require('../utils/CustomError');
require('dotenv').config();
const { Kafka } = require('@confluentinc/kafka-javascript').KafkaJS;

const highlightRouting = asyncErrorHandler(async (req, res, next) => {
    
    const user_id = req.body.id;
    const message = req.body.message;

    const kafka_message = { user_id: user_id, content: message, timestamp: (Date.now()).toString() };
    const partition = (user_id % 3).toString();

    let producer;

    let consumer;
    let stopped = false;

    try {
        consumer = new Kafka().consumer({
            'bootstrap.servers': process.env.KAFKA_BROKERS_EXTERNAL,
            'group.id': 'test',
            'auto.offset.reset': 'latest',
        });

        await consumer.connect();
        await consumer.subscribe({ topics: ["test"] });

        producer = new Kafka().producer({
            'bootstrap.servers': process.env.KAFKA_BROKERS_EXTERNAL,
        });


        await producer.connect();

        const deliveryReports = await producer.send({
            topic: 'highlight',
            messages: [
                { value: Buffer.from(JSON.stringify(kafka_message), 'utf-8'), partition: 2, key: partition },]
        });

        await producer.disconnect();
        let data;
        
          consumer.run({
            eachMessage: async ({ topic, partition, message }) => {
              let checked = JSON.parse(message.value.toString());
              if(checked.user_id == user_id) {
                stopped = true;
                data = checked
              }
              console.log({
                topic,
                partition,
                offset: message.offset,
                key: message.key?.toString(),
                value: JSON.parse(message.value.toString()),
              });
            }
          });
        
        let count = 0;

        while(!stopped) {
            console.log(count++);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }

        await consumer.disconnect();

        res.status(200).json({payload: data});

    } catch (err) {
        const error = new CustomError('Kafka Producer Error', 100, err);
        console.log(err);
        await producer.disconnect;
        await consumer.disconnect;
        next(error);
    }
});


module.exports = {highlightRouting};