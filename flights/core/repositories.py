from abc import ABC, abstractmethod

from flights.core.models import FlightEvent


class JourneysRepository(ABC):

    @abstractmethod
    def get_flight_events(self) -> list[FlightEvent]:
        pass
