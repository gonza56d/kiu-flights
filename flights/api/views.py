from datetime import date

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from flights.api.models import SearchJourneysRequest, SearchJourneysResponse
from flights.containers import FlightsContainer, FlightsCommandBus

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
        command_bus: FlightsCommandBus = Depends(Provide[FlightsContainer.command_bus]),
):
    action = SearchJourneysRequest(
        from_=origin,
        to=destination,
        date=date,
    ).get_action()
    return command_bus.handle(action)
