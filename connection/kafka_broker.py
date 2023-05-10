from supporting import env
from confluent_kafka import Producer


producer = Producer({
    "bootstrap.servers": f"{env.KAFKA_HOST}:{env.KAFKA_PORT}"
})