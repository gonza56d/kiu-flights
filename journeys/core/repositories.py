from abc import ABC, abstractmethod

from journeys.core.models import FlightEvent


class FlightsRepository(ABC):
    """
    Abstract base class for a flights' repository.

    Implementations should provide a way to fetch flight events
    from a data source (e.g., HTTP API, database, or cache)
    """

    @abstractmethod
    def get_flight_events(self) -> list[FlightEvent]:
        pass
