import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from app.messaging.rabbitmq.connection import get_rabbit_connection

load_dotenv()

MQ_PRODUCT_ROUTING_KEY = os.getenv("MQ_PRODUCT_ROUTING_KEY")


if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


class Consumer:
    @staticmethod
    async def process_delete_product(
            channel: "BlockingChannel",
            method: "Basic.Deliver",
            properties: "BasicProperties",
            body: bytes
    ):
        print("Message recieved")
        print(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    @staticmethod
    async def consume_product_delete():
        with get_rabbit_connection() as connection:
            with connection.channel() as channel:
                channel.basic_consume(
                    queue=f"{MQ_PRODUCT_ROUTING_KEY}.delete",
                    on_message_callback=Consumer.process_delete_product,
                )
                #блокирует поток, поэтому ответ не доходит, нужно сделать async
                channel.start_consuming()
