from aio_pika.abc import AbstractIncomingMessage
from app.messaging.rabbitMQ.session import RabbitMQSession


async def on_message(message: AbstractIncomingMessage) -> None:
    print(" [x] Received message %r" % message)
    print("Message body is: %r" % message.body)


async def get_category_msq():
    try:
        async with RabbitMQSession() as channel:
            routing_key = "category"

            queue = await channel.declare_queue("category")

            await queue.consume(on_message, no_ack=True)
            return True
    except Exception as e:
        print(e)
        return False
