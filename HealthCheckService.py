import json
import requests
import schedule
import time
from confluent_kafka import Producer

class HealthCheckService:
    def __init__(self, kafka_broker, topic, services):
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.services = services
        self.producer = Producer({'bootstrap.servers': kafka_broker})

    def check_service_health(self, url):
        try:
            response = requests.get(url)
            status = 'healthy' if response.status_code == 200 else 'unhealthy'
        except requests.exceptions.RequestException:
            status = 'unhealthy'
        return status

    def produce_health_status(self):
        for service, url in self.services.items():
            status = self.check_service_health(url)
            message = {'service': service, 'status': status}
            self.producer.produce(self.topic, json.dumps(message))
            self.producer.flush()

    def run(self):
        schedule.every(60).seconds.do(self.produce_health_status)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    services = {
        'service1': 'cluster-kafka-controller-0.cluster-kafka-controller-headless.dk.svc.cluster.local:9092',
        'service2': 'cluster-kafka-controller-1.cluster-kafka-controller-headless.dk.svc.cluster.local:9092',
        'service3': 'cluster-kafka-controller-2.cluster-kafka-controller-headless.dk.svc.cluster.local:9092'
    }
    kafka_broker = 'localhost:9092'
    topic = 'health_checks_topic'

    health_check_service = HealthCheckService(kafka_broker, topic, services)
    health_check_service.run()
