"""Module for managing RabbitMQ connection."""
from contextlib import asynccontextmanager
from types import TracebackType
from typing import AsyncIterator

import aio_pika
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from app.config import settings


class RabbitMQConnectionManager:

    def __init__(self) -> None:
        self.__connection: AbstractRobustConnection | None = None

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: "
            f"connection={self.__connection}>"
        )

    async def _create_connection(self, timeout: int = 10) -> None:
        self.__connection = await aio_pika.connect_robust(
            settings.rabbitmq.rabbitmq_url,
            timeout=timeout,
        )

    async def _close_connection(self) -> None:
        if self.__connection is not None:
            await self.__connection.close()
            self.__connection = None

    async def check_connection(self) -> AbstractRobustConnection:
        if self.__connection is None:
            raise RuntimeError("Connection not created")
        return self.__connection

    @asynccontextmanager
    async def channel(self) -> AsyncIterator[AbstractChannel]:
        connection = await self.check_connection()
        channel = await connection.channel()
        try:
            yield channel
        finally:
            await channel.close()

    async def __aenter__(self) -> "RabbitMQConnectionManager":
        await self._create_connection()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self._close_connection()
