
from dataclasses import dataclass
from cache_refresher.repositories import CacheRepository
from journeys.core.repositories import JourneysRepository


@dataclass
class CacheRefresher:

    journey_repository: JourneysRepository
    cache_repository: CacheRepository

    def run(self) -> None:
        results = self.journey_repository.get_flight_events()
        self.cache_repository.refresh_cache(results)

