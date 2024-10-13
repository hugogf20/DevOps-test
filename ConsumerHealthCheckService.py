import json
from confluent_kafka import Consumer, KafkaException, KafkaError

class ConsumerHealthCheckService:
    def __init__(self, kafka_broker, group_id, topic):
        self.kafka_broker = kafka_broker
        self.group_id = group_id
        self.topic = topic
        self.consumer = Consumer({
            'bootstrap.servers': kafka_broker,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })

    def consume_messages(self):
        self.consumer.subscribe([self.topic])
        
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        print(f"Reached end of partition: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    # Properly formatted JSON message expected
                    message = json.loads(msg.value().decode('utf-8'))
                    self.process_message(message)
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()

    def process_message(self, message):
        service = message.get('service')
        status = message.get('status')
        print(f"Received health check for {service}: {status}")

if __name__ == '__main__':
    kafka_broker = 'localhost:9092'
    group_id = 'health_check_group'
    topic = 'health_checks_topic'

    consumer_service = ConsumerHealthCheckService(kafka_broker, group_id, topic)
    consumer_service.consume_messages()
