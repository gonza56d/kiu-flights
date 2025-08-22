from dataclasses import dataclass

from flights.core.models import FlightEvent
from flights.core.repositories import JourneysRepository


@dataclass
class JourneysHTTPRepository(JourneysRepository):
    """Implement JourneyRepository interface with a REST provider through HTTP."""

    provider_base_url: str
    endpoint: str

    def get_flight_events(self) -> list[FlightEvent]:
        raise Exception('This is working')
