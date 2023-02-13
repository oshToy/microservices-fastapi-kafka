# python -m pytest

import datetime
import uuid

import pytest
import pytest_mock
from httpx import AsyncClient
from main import app

ID = uuid.uuid4()
HTML_URL = "https://www.google.com/"
CREATE_AT = datetime.datetime.now()


@pytest.mark.anyio
async def test_get_undefined():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 404


async def get_valid_all_crawlers():
    return [{"id": ID, "html_url": HTML_URL, "create_at": CREATE_AT}]


@pytest.mark.anyio
async def test_get_undefined(mocker: pytest_mock.MockerFixture):
    from service import CrawlerRequestService

    async with AsyncClient(app=app, base_url="http://test") as ac:
        mocker.patch.object(
            CrawlerRequestService, "get_all_crawlers", new=get_valid_all_crawlers
        )
        response = await ac.get("/crawler")
    assert response.json()[0]["id"] == str(ID)
    assert response.status_code == 200
