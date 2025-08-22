from dataclasses import asdict
import json

from redis import Redis

from cache_refresher.repositories import CacheRepository
from flights.core.models import FlightEvent


class RedisCacheRepository(CacheRepository):

    def __init__(self, repository_uri: str, cache_key: str):
        self._connection = Redis.from_url(repository_uri)
        self._connection.ping()
        self._cache_key = cache_key

    def refresh_cache(self, results: list[FlightEvent]) -> None:
        self._connection.set(
            self._cache_key,
            json.dumps([asdict(flight_event) for flight_event in results]),
        )
