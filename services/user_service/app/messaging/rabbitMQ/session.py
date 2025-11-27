import os
import aio_pika
import aio_pika.abc

class RabbitMQSession:
    def __init__(self):
        self.rabbitmq_url = os.getenv("RABBITMQ_URL")
        self.connection = None
        self.channel = None

    async def __aenter__(self):
        self.connection: aio_pika.abc.AbstractRobustConnection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        return self.channel  # Возвращаем канал, с которым удобно работать

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()
        await self.connection.close()