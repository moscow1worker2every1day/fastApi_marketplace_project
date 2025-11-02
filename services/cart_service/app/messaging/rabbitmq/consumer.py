from faststream.rabbit import RabbitBroker

from app.logging import logging

broker = RabbitBroker()


@broker.subscriber("products_check")
async def consume_cart_msg(msq: str):
    async with broker:
        await broker.start()
        logging.info("Rabbitmq start")

    logging.info("Rabbitmq end")
