"""
import pytest
from httpx import ASGITransport, AsyncClient

from api.main import api


@pytest.fixture()
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=api),
        base_url='http://localhost:8000/api/v1'
    ) as ac:
        yield ac

"""