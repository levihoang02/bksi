from confluent_kafka import Consumer, KafkaException, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
import json

class KafkaConsumerService:
    def __init__(self, topics, group_id=None, servers=None):
        self.topic = topics
        self.group_id = group_id
        self.servers = servers

        self.config = {
            'bootstrap.servers': self.servers,
            'group.id': self.group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False  # Disable auto commit for better control
        }
        self.consumer = Consumer(self.config)
        self.consumer.subscribe([self.topic])

    def consume_messages(self, process_function):
        """ Continuously consume messages and apply a processing function """
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                if msg.error():
                    print(f"Consumer error: {msg.error()}")
                    continue
                
                try:
                    # Decode bytes to string and parse JSON
                    message_str = msg.value().decode("utf-8")
                    message_data = json.loads(message_str)
                    print(message_data)
                    # Process the parsed message using the provided function
                    try:
                        process_function(message_data)
                    except Exception as e:
                        continue
                    finally:
                        self.consumer.commit(msg)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    continue

        except KeyboardInterrupt:
            print("Stopping consumer...")

        finally:
            self.consumer.close()
            
    def _close(self):
        self.consumer.close()
        
def create_topic_configs(consumer_topics, dlq_topic, dlq_replicas=3, dlq_partitions=3, replicas=3, partitions=3):
    """ Generate a list of topic configurations including DLQ_TOPIC """
    
    # Create topic_configs list based on the consumer_topics array
    topic_configs = [{'topic': topic, 'replicas': replicas, 'partitions': partitions} for topic in consumer_topics]
    
    # Add the DLQ topic configuration with specific replicas and partitions
    dlq_topic_config = {'topic': dlq_topic, 'replicas': dlq_replicas, 'partitions': dlq_partitions}
    topic_configs.append(dlq_topic_config)
    
    return topic_configs

def seed_topics(brokers, topic_configs):
    """ Check if topics exist, create them if not based on given configurations """
    admin_client = AdminClient({'bootstrap.servers': brokers})
    try:
        existing_topics = admin_client.list_topics(timeout=10).topics

        topics_to_create = []
        for config in topic_configs:
            topic = config['topic']
            replicas = config.get('replicas', 3)
            partitions = config.get('partitions', 1)

            if topic not in existing_topics:
                print(f"Topic '{topic}' does not exist. Creating it...")
                new_topic = NewTopic(topic, num_partitions=partitions, replication_factor=replicas)
                topics_to_create.append(new_topic)
            else:
                print(f"Topic '{topic}' already exists.")

        if topics_to_create:
            futures = admin_client.create_topics(topics_to_create)
            for topic, future in futures.items():
                try:
                    future.result()  # Block until topic is actually created
                    print(f"Topic '{topic}' created successfully.")
                except Exception as e:
                    err = e.args[0]
                    if isinstance(err, KafkaError) and err.code() == KafkaError.TOPIC_ALREADY_EXISTS:
                        print(f"Topic '{topic}' already exists. Ignoring.")
                    else:
                        print(f"Failed to create topic '{topic}': {e}")
                    print(f"Failed to create topic '{topic}': {e}")
        else:
            print("No topics needed to be created.")

    except KafkaException as e:
        print(f"Error while checking/creating topics: {e}")