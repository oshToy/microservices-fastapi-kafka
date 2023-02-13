import logging
from typing import Optional, Dict
from fastapi import APIRouter
from service import CrawlStatusService, InsertResponse
from pydantic import BaseModel, UUID4, HttpUrl
import metrics as metrics
from models import Status
from fastapi.encoders import jsonable_encoder

router = APIRouter()

crawl_status_service = CrawlStatusService()


class CrawlStatusRequest(BaseModel):
    status: Optional[Status] = Status.Accepted.value
    file_path: Optional[HttpUrl]

    class Config:
        schema_extra = {
            "example": {
                "file_path": None,
                "status": "Accepted",
            }
        }


class CrawlStatusPostRequest(CrawlStatusRequest):
    id: UUID4


@router.post("/status", tags=["status"])
async def post_crawler_status(crawl_status: CrawlStatusPostRequest) -> InsertResponse:
    metrics.POST_CRAWLER_STATUS_CNT.inc()
    return await crawl_status_service.save_crawler_status(
        status_id=crawl_status.id,
        file_path=crawl_status.file_path,
        status=crawl_status.status,
    )


@router.put("/status/{status_id}", tags=["status"])
async def update_item(status_id: str, crawl_status: CrawlStatusRequest):
    metrics.PUT_CRAWLER_STATUS_CNT.inc()
    return await crawl_status_service.update_crawler_status(
        status_id=status_id, **jsonable_encoder(crawl_status)
    )


@router.get("/status/{status_id}", tags=["status"])
async def get_crawler_by_id(status_id: UUID4) -> Dict:
    metrics.GET_CRAWLER_STATUS_BY_ID_CNT.inc()
    return await crawl_status_service.get_crawler_status_by_id(status_id)
