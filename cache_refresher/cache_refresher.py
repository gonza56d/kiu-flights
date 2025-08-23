from dataclasses import dataclass
from cache_refresher.repositories import CacheRepository
from journeys.core.repositories import FlightsRepository


@dataclass
class CacheRefresher:

    flights_repository: FlightsRepository
    cache_repository: CacheRepository

    def run(self) -> None:
        results = self.flights_repository.get_flight_events()
        self.cache_repository.refresh_cache(results)

