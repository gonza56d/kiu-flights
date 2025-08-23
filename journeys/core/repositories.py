from abc import ABC, abstractmethod

from journeys.core.models import FlightEvent


class JourneysRepository(ABC):

    @abstractmethod
    def get_flight_events(self) -> list[FlightEvent]:
        pass
