import json
import os
from dotenv import load_dotenv
from typing import TYPE_CHECKING
from app.logging import log
from app.messaging.rabbitMQ.connection import get_rabbit_connection
from app.schemas.product import GetProduct

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingConnection

load_dotenv()

MQ_PRODUCT_EXCHANGE = os.getenv("MQ_PRODUCT_EXCHANGE")
MQ_PRODUCT_ROUTING_KEY = os.getenv("MQ_PRODUCT_ROUTING_KEY")


class Publisher:

    @staticmethod
    async def publish_product_change(product: GetProduct, key_msg: str):
        with get_rabbit_connection() as connection:
            with connection.channel() as channel:
                log.info("RabbitMQ channel created")
                try:
                    queue = channel.queue_declare(queue=f"{MQ_PRODUCT_ROUTING_KEY}.{key_msg}")
                    body = json.dumps({
                        "event": f"{MQ_PRODUCT_ROUTING_KEY}.{key_msg}",
                        "id": product.id,
                        "name": product.name,
                        "description": product.description,
                        "price": product.price,
                        "category_id": product.category_id,
                        "stock": product.stock,
                        "available": product.available,
                    }).encode("utf-8")

                    channel.basic_publish(
                        exchange="",
                        routing_key=f"{MQ_PRODUCT_ROUTING_KEY}.{key_msg}",
                        body=body
                    )

                    return True
                except Exception as e:
                    return False
