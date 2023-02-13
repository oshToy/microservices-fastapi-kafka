from typing import List, Dict
from fastapi import APIRouter
from service import CrawlerRequestService, InsertResponse
from pydantic import BaseModel, HttpUrl, UUID4
import metrics as metrics


router = APIRouter()

crawl_service = CrawlerRequestService()


class CrawlRequest(BaseModel):
    html_url: HttpUrl

    class Config:
        schema_extra = {
            "example": {
                "html_url": "https://www.google.com/",
            }
        }


@router.post("/crawler", tags=["crawler"])
async def post_crawler(crawl_request: CrawlRequest) -> InsertResponse:
    metrics.POST_CRAWLER_CNT.inc()
    return await crawl_service.save_crawler(crawl_request.html_url)


@router.get("/crawler/{crawler_id}", tags=["crawler"])
async def get_crawler_by_id(crawler_id: UUID4) -> Dict:
    metrics.GET_CRAWLER_BY_ID_CNT.inc()
    return await crawl_service.get_crawler_by_id(crawler_id)


@router.get("/crawler", tags=["crawler"])
async def get_all_crawlers() -> List[Dict]:
    metrics.GET_ALL_CRAWLERS_CNT.inc()
    return await crawl_service.get_all_crawlers()
