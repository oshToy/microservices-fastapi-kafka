import datetime
from typing import List, Dict
from fastapi import APIRouter
import config_loader as config_loader
import metrics
from service import CrawlerRequestService
from pydantic import BaseModel, HttpUrl, UUID4

config = config_loader.Config()

router = APIRouter()


class CrawlRequest(BaseModel):
    html_url: HttpUrl

    class Config:
        schema_extra = {
            "example": {
                "html_url": "https://www.google.com/",
            }
        }


class PostResponse(BaseModel):
    id: UUID4
    html_url: HttpUrl
    create_at: datetime.datetime


@router.post("/crawler", tags=["crawler"])
async def post_crawler(crawl_request: CrawlRequest) -> None:
    metrics.POST_CRAWLER_CNT.inc()
    return await CrawlerRequestService.save_crawler(crawl_request.html_url)


@router.get("/crawler/{crawler_id}", tags=["crawler"])
async def get_crawler_by_id(crawler_id: UUID4) -> Dict:
    metrics.GET_CRAWLER_BY_ID_CNT.inc()
    return await CrawlerRequestService.get_crawler_by_id(crawler_id)


@router.get("/crawler", tags=["crawler"])
async def get_all_crawlers() -> List[Dict]:
    metrics.GET_ALL_CRAWLERS_CNT.inc()
    return await CrawlerRequestService.get_all_crawlers()
