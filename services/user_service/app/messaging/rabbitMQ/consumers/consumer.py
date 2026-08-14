import asyncio
import json
from uuid import UUID

from aio_pika import Message
from aio_pika.abc import AbstractChannel, AbstractIncomingMessage
from sqlalchemy.exc import NoResultFound

from app.log import startup_logger
from app.services.user_service import UserService
from app.storage.postgresql.connection import DatabaseManager
from app.storage.postgresql.repositories.user_repository import UserRepository


QUEUE_NAME = "user.get_user_by_id.seller"
_reply_channel: AbstractChannel | None = None


async def handle_get_user_by_id(message: AbstractIncomingMessage) -> None:
    payload = json.loads(message.body.decode())
    user_id = UUID(payload["user_id"])
    required_role = payload["required_role"]
    startup_logger.info(
        f"RabbitMQ request received: user_id={user_id}, required_role={required_role}"
    )

    try:
        async with DatabaseManager.session_factory() as session:
            user = UserService._to_get_user(
                await UserRepository.get_user_by_id(session, user_id)
            )

        if user.role.value != required_role:
            body = {"detail": f"User have not role {required_role}"}
        else:
            body = {"user": user.model_dump(mode="json")}
    
    except asyncio.TimeoutError:
        body = {"detail": "Database timeout while getting user"}
    except NoResultFound:
        body = {"detail": "User not found"}
    except Exception as e:
        body = {"detail": f"Error getting user: {type(e).__name__} - {e}"}

    if message.reply_to:
        await _reply_channel.default_exchange.publish(
            Message(
                body=json.dumps(body).encode(),
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to,
        )
        startup_logger.info(
            f"RabbitMQ response sent to {message.reply_to} "
            f"for user_id={user_id}"
        )
    await message.ack()


async def start_user_service_consumer() -> None:
    from app.main import app
    global _reply_channel

    connection = await app.state.rabbitmq_connection.check_connection()
    channel = await connection.channel()
    _reply_channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(handle_get_user_by_id)
    startup_logger.info(f"RabbitMQ consumer listening on queue '{QUEUE_NAME}'")
    await asyncio.Event().wait()
