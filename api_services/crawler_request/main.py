import uvicorn
import logging
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics
import core.config_loader as config_loader
from db import DB
from models import Base
import routes

config = config_loader.Config()

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


# TODO ONLY DEV !!!
@app.on_event("startup")
async def init_tables():
    async with DB().db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    logger.info("Starting server")
    logger.warning("To start server use command: uvicorn main:app --reload")
    uvicorn.run(
        app,
        port=config.get(config_loader.WEB_PORT),
        host=config.get(config_loader.WEB_HOST),
    )
