import pika
from dotenv import load_dotenv
import os

load_dotenv()

connection_params = pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST"), port=int(os.getenv("RABBITMQ_PORT")))


def get_rabbit_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(
        parameters=connection_params,
    )
