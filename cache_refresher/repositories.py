from abc import ABC, abstractmethod

from journeys.core.models import FlightEvent


class CacheRepository(ABC):

    repository_uri: str

    @abstractmethod
    def refresh_cache(self, results: list[FlightEvent]) -> None:
        pass
