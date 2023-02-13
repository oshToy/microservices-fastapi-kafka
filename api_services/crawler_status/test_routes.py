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
