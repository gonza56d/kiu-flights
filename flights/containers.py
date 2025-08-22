"""Declarative IoC layer."""
from typing import Any

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Factory

from flights.api.repositories import JourneysHTTPRepository
from flights.core.actions import SearchJourneys
from flights.core.handlers import SearchJourneysHandler
from flights.core.repositories import JourneysRepository


class FlightsCommandBus:
    _commands = {}
    def __init__(self, bus: dict[Any, Any]):
        for action, handler in bus.items():
            FlightsCommandBus._commands[action.provides.__name__] = handler

    def handle(self, action) -> Any:
        command = FlightsCommandBus._commands[action.__class__.__name__]()
        return command(action)


class FlightsContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(modules=[
        'flights.api.models',
        'flights.api.repositories',
        'flights.api.views',
        'flights.core.actions',
        'flights.core.handlers',
        'flights.core.models',
        'flights.core.repositories',
    ])
    config = Configuration()
    journeys_repository: Factory[JourneysRepository] = Factory(
        JourneysHTTPRepository,
        provider_base_url=config.journeys_provider_base_url,
        endpoint=config.journeys_provider_endpoint_v1,
    )
    command_bus: Factory[FlightsCommandBus] = Factory(
        FlightsCommandBus,
        {
            Factory(SearchJourneys): Factory(
                SearchJourneysHandler,
                journeys_repository=journeys_repository,
            )
        }
    )
