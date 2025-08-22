from dataclasses import dataclass

from flights.core.actions import SearchJourneys
from flights.core.models import Journey
from flights.core.repositories import JourneysRepository


@dataclass
class SearchJourneysHandler:

    journeys_repository: JourneysRepository

    def __call__(self, action: SearchJourneys) -> list[Journey]:
        pass
