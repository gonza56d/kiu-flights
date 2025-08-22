from datetime import datetime
from http import HTTPStatus
import requests

from dataclasses import dataclass

from flights.core.models import FlightEvent
from flights.core.repositories import JourneysRepository


@dataclass
class JourneysHTTPRepository(JourneysRepository):
    """Implement JourneyRepository interface with a REST provider through HTTP."""

    provider_base_url: str
    endpoint: str

    def get_flight_events(self) -> list[FlightEvent]:
        response = requests.get(url=f'{self.provider_base_url}{self.endpoint}')
        if response.status_code != HTTPStatus.OK:
            pass
        return [
            FlightEvent(
                flight_number=result['flight_number'],
                from_=result['departure_city'],
                to=result['arrival_city'],
                departure_time=datetime.fromisoformat(result['departure_datetime'].replace('Z', '+00:00')),
                arrival_time=datetime.fromisoformat(result['arrival_datetime'].replace('Z', '+00:00')),
            )
            for result in response.json()
        ]
