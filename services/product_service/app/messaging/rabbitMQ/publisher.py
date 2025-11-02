from faststream.rabbit.fastapi import RabbitRouter

from app.logging import logging
from app.storage.postgresql.repositories.product_repository import ProductRepository

router = RabbitRouter()


async def publish_product_change(msg: str):
    router.broker.publish(
        message=msg,
        queue="products_check"
    )

