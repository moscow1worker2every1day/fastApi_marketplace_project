import asyncio
import json
import uuid
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from fastapi import HTTPException, status


class UserServicePublisher:
    """
    Class for requesting user service.
    Publish messages to user service.
    """

    QUEUE_NAME = "user.get_user_by_id.seller"
    TIMEOUT = 10

    @classmethod
    async def publish_user_request(cls, user_id: UUID, required_role: str) -> dict:
        from app.main import app

        rabbitmq_connection = app.state.rabbitmq_connection
        async with rabbitmq_connection.channel() as channel:
            await channel.declare_queue(cls.QUEUE_NAME, durable=True)
            callback_queue = await channel.declare_queue(exclusive=True)

            correlation_id = str(uuid.uuid4())
            loop = asyncio.get_running_loop()
            future: asyncio.Future = loop.create_future()

            async def on_response_callback(message: AbstractIncomingMessage) -> None:
                if message.correlation_id == correlation_id and not future.done():
                    future.set_result(json.loads(message.body.decode()))

            await callback_queue.consume(on_response_callback, no_ack=True)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(
                        {
                            "user_id": str(user_id),
                            "required_role": required_role,
                        }
                    ).encode(),
                    correlation_id=correlation_id,
                    reply_to=callback_queue.name,
                ),
                routing_key=cls.QUEUE_NAME,
            )

            try:
                return await asyncio.wait_for(future, timeout=cls.TIMEOUT)
            except asyncio.TimeoutError:
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail="Timeout waiting for response from user service",
                    headers={"Timeout": str(cls.TIMEOUT)},
                )
