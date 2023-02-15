import uvicorn
import logging
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics
import os
import core.config_loader as config_loader

config_abs_path = "/".join(os.path.abspath(__file__).split("/")[0:-1])
config = config_loader.Config(
    env_namespace="API_CRAWLER_REQUEST",
    config_file_path=f"{config_abs_path}/config.yml",
)

from core.db import DB
from core.aio_kafka import AioProducer
from models import Base
import routes

logging.basicConfig(level=config.get(config_loader.LOGGING_LEVEL))
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="CRAWL REQUEST")
app.include_router(routes.router)

# METRICS TO Prometheus
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


@app.get("/healthcheck", include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.on_event("startup")
async def init_tables():
    # TODO ONLY DEV !!!
    async with DB().db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    # kafka producer
    await AioProducer().start()


@app.on_event("shutdown")
async def shutdown_event():
    await AioProducer().stop()
    await DB().db_engine.dispose()


if __name__ == "__main__":
    logger.info("Starting server")
    logger.warning("To start server use command: uvicorn main:app --reload")
    uvicorn.run(
        app,
        port=config.get(config_loader.WEB_PORT),
        host=config.get(config_loader.WEB_HOST),
    )
