import os

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

class RabbitmqService:
    @staticmethod
    async def check_connection(logging, retries=10, delay=3):
        for i in range(retries):
            try:
                connection = await aio_pika.connect_robust(RABBITMQ_URL)
                logging.info("Connected to RabbitMQ successfull")
                print("Connected to RabbitMQ successfull")
                await connection.close()
                return True
            except Exception as e:
                print(f"Failed to connect to RabbitMQ: {e}")
                logging.warning(f"Failed to connect to RabbitMQ: {e}")
                logging.warning(f"Waiting for RabbitMQ... retry {i + 1}/{retries}")
                await asyncio.sleep(delay)
        return False