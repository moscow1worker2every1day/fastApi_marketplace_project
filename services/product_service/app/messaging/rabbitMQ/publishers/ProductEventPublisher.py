import json

import aio_pika
from aio_pika import ExchangeType

from app.config import settings
from app.log import products_logger
from app.storage.postgresql.models.product_model import ProductOrm


class ProductEventPublisher:
    """Publish product domain events for cart and other consumers."""

    @classmethod
    async def publish_product_change(cls, product: ProductOrm, event: str) -> None:
        """
        Publish a product event to the Product topic exchange.

        ``event`` examples: ``product.deleted``, ``product.unavailable``, ``product.updated``.
        """
        from app.main import app
        payload = {
            "event": event,
            "product_id": str(product.id),
            "price": product.price,
            "available": product.available,
            "name": product.name,
        }

        rabbitmq_connection = app.state.rabbitmq_connection
        async with rabbitmq_connection.channel() as channel:
            exchange = await channel.declare_exchange(
                settings.rabbitmq.mq_product_exchange,
                ExchangeType.TOPIC,
                durable=True,
            )
            await exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=event,
            )

        products_logger.info(
            f"Published product event {event} for product_id={product.id}"
        )
