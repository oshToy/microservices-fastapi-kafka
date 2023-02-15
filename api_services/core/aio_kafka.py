import logging
from core.singleton import MetaSingleton
from core import config_loader as config_loader
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
import asyncio
from typing import Union, Callable

logger = logging.getLogger(__name__)
config = config_loader.Config()


class AioProducer(metaclass=MetaSingleton):
    def __init__(self):
        self.aio_producer: AIOKafkaProducer = self.__init_producer()

    def __init_producer(self) -> AIOKafkaProducer:
        return AIOKafkaProducer(
            bootstrap_servers=config.get(config_loader.KAFKA_BROKER),
            key_serializer=self.__string_serializer,
            value_serializer=self.__json_serializer,
        )

    def __string_serializer(self, value: Union[str, None]):
        if value is None:
            return
        return value.encode()

    async def start(self):
        await self.aio_producer.start()

    async def stop(self):
        await self.aio_producer.stop()

    def __json_serializer(self, value: str):
        return json.dumps(value).encode()

    async def produce_message_and_wait_for_ack(
        self, topic: str, message: dict, key: str = None
    ):
        ack = await self.aio_producer.send_and_wait(topic, message, key=key)
        logger.info(ack)


class AioConsumer(metaclass=MetaSingleton):
    def __init__(
        self, *topics, loop=None, group_id: str = "", manual_commit: bool = False
    ):
        self.aio_consumer: AIOKafkaConsumer = self.__init_consumer(
            *topics, group_id=group_id, loop=loop, manual_commit=manual_commit
        )
        self.aio_consumer_task: Union[asyncio.Task, None] = None
        self.manual_commit: bool = manual_commit

    def __init_consumer(
        self, *topics, loop, group_id: str, manual_commit: bool
    ) -> AIOKafkaConsumer:
        return AIOKafkaConsumer(
            *topics,
            loop=loop,
            bootstrap_servers=config.get(config_loader.KAFKA_BROKER),
            group_id=group_id,
            key_deserializer=self.__string_deserializer,
            value_deserializer=self.__json_deserializer,
            enable_auto_commit=not manual_commit,
        )

    def __string_deserializer(self, value: bytes):
        return value.decode()

    def __json_deserializer(self, value: bytes):
        return json.loads(value.decode())

    async def start(self):
        await self.aio_consumer.start()

    async def stop(self):
        await self.aio_consumer.stop()

    def cancel_task(self):
        self.aio_consumer_task.cancel()

    async def consume(self, async_function: Callable):
        self.aio_consumer_task = asyncio.create_task(
            self.consume_messages(async_function)
        )

    async def consume_messages(self, async_function: Callable):
        # msg.topic, msg.partition, msg.offset, msg.key, msg.value, msg.timestamp

        async for msg in self.aio_consumer:
            logger.info(
                f"Message Consumed: {msg.topic}, {msg.partition},{msg.offset}, {msg.key}, {msg.value}, {msg.timestamp}"
            )
            await async_function(msg)
            if self.manual_commit:
                # huge performance tradeoff !
                # https://aiokafka.readthedocs.io/en/stable/examples/manual_commit.html
                await self.aio_consumer.commit()
                logger.info(f"Message Commited  {msg.key, msg.value, msg.timestamp}")
