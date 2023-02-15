import uvicorn
import logging
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics
import asyncio
import core.config_loader as config_loader
import os

config_abs_path = "/".join(os.path.abspath(__file__).split("/")[0:-1])
config = config_loader.Config(
    env_namespace="API_CRAWLER_STATUS", config_file_path=f"{config_abs_path}/config.yml"
)

from core.aio_kafka import AioConsumer
from core.db import DB
from models import Base
import routes
from typing import Union

# global variable
aio_consumer: Union[AioConsumer, None] = None

logging.basicConfig(level=config.get(config_loader.LOGGING_LEVEL))
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="CRAWL STATUS")
app.include_router(routes.router)

# METRICS TO Prometheus
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.on_event("shutdown")
async def shutdown_event():
    aio_consumer.cancel_task()
    await aio_consumer.stop()
    await DB().db_engine.dispose()


@app.on_event("startup")
async def startup_event():
    # TODO ONLY DEV !!!
    async with DB().db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # kafka consumer
    await init_kafka_consumer()


async def init_kafka_consumer():
    loop = asyncio.get_event_loop()
    global aio_consumer
    aio_consumer = AioConsumer(
        config.get(config_loader.CRAWLER_STATUS_TOPIC),
        loop=loop,
        group_id=config.get(config_loader.CONSUMER_GROUP_ID),
        manual_commit=True,
    )
    await aio_consumer.start()
    await aio_consumer.consume(routes.handle_status_updates)


# todo export the server activation to core class
if __name__ == "__main__":
    logger.info("Starting server")
    logger.warning("To start server use command: uvicorn main:app --reload")
    uvicorn.run(
        app,
        port=config.get(config_loader.WEB_PORT),
        host=config.get(config_loader.WEB_HOST),
    )
