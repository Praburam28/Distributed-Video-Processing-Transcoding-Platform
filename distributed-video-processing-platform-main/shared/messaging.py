import json
import aio_pika
from shared.config import settings

async def publish(queue_name: str, payload: dict, routing_key: str | None = None):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.declare_queue(queue_name, durable=True)
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await channel.default_exchange.publish(message, routing_key or queue_name)

async def consume(queue_name: str, callback):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)
    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.consume(callback)
    return connection
