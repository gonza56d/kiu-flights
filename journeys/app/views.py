from datetime import date

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from journeys.app.models import FlightEvent, SearchJourneysRequest, SearchJourneysResponse
from journeys.core.models import Journey
from journeys.containers import JourneysContainer, JourneysCommandBus

router = APIRouter(
    prefix='/journeys',
    tags=['journeys']
)

@router.get('/search', response_model=list[SearchJourneysResponse])
@inject
async def search_journeys(
        date: date,
        origin: str,
        destination: str,
        command_bus: JourneysCommandBus = Depends(Provide[JourneysContainer.command_bus]),
):
    """
    Search journeys available for given date, with the right origin and destinations.

    Args:
        date (date): The desired date of departure.
        origin (str): 3-letter code indicating city of departure.
        destination (str): 3-letter code indicating city of destination.

    Returns:
        list[SearchJourneysResponse]: n possible journeys, from which each of these
        can have 1 or 2 flight events connected.
    """
    action = SearchJourneysRequest(
        from_=origin,
        to=destination,
        date=date,
    ).get_action()
    results: list[Journey] = command_bus.handle(action)
    return [
        SearchJourneysResponse(
            connections=result.connections,
            path=[FlightEvent(
                **{
                    'flight_number': flight_event.flight_number,
                    'from': flight_event.from_,
                    'to': flight_event.to,
                    'departure_time': flight_event.departure_time,
                    'arrival_time': flight_event.arrival_time,
                }
            ) for flight_event in result.flight_events],
        )
        for result in results
    ]
