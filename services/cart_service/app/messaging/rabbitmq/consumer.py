import asyncio
import json
from uuid import UUID

from aio_pika import ExchangeType
from aio_pika.abc import AbstractIncomingMessage

from app.config import settings
from app.log import cart_logger
from app.services.cart_service import UserCartService


async def handle_product_event(message: AbstractIncomingMessage) -> None:
    async with message.process():
        payload = json.loads(message.body.decode())
        event = payload.get("event") or message.routing_key or ""
        product_id = UUID(payload["product_id"])
        price = payload.get("price")
        available = payload.get("available")

        cart_logger.info(
            "Product event received: event=%s product_id=%s",
            event,
            product_id,
        )
        affected = await UserCartService.handle_product_event(
            product_id=product_id,
            event=event,
            price=price,
            available=available,
        )
        cart_logger.info(
            "Product event handled: event=%s product_id=%s affected_carts=%s",
            event,
            product_id,
            affected,
        )


async def start_product_events_consumer() -> None:
    from app.main import app

    connection = await app.state.rabbitmq_connection.check_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        settings.rabbitmq.mq_product_exchange,
        ExchangeType.TOPIC,
        durable=True,
    )
    queue = await channel.declare_queue(
        settings.rabbitmq.mq_cart_queue,
        durable=True,
    )
    await queue.bind(exchange, routing_key=f"{settings.rabbitmq.mq_product_routing_key}.#")
    await queue.consume(handle_product_event)

    cart_logger.info(
        "RabbitMQ consumer listening on queue '%s' (exchange=%s, binding=%s.#)",
        settings.rabbitmq.mq_cart_queue,
        settings.rabbitmq.mq_product_exchange,
        settings.rabbitmq.mq_product_routing_key,
    )
    await asyncio.Event().wait()
