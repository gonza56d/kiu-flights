from datetime import date, datetime

from pydantic import BaseModel, Field

from journeys.core.actions import SearchJourneys


class SearchJourneysRequest(BaseModel):

    from_: str = Field(..., max_length=3, min_length=3)
    to: str = Field(..., max_length=3, min_length=3)
    date: date

    def get_action(self):
        return SearchJourneys(**self.model_dump())


class FlightEvent(BaseModel):

    flight_number: str = Field(..., max_length=6, min_length=6)
    from_: str = Field(..., max_length=3, min_length=3, alias='from')
    to: str = Field(..., max_length=3, min_length=3)
    departure_time: datetime
    arrival_time: datetime


class SearchJourneysResponse(BaseModel):

    connections: int
    path: list[FlightEvent]
