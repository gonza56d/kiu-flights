"""Declarative IoC layer."""
from typing import Any

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Factory

from flights.core.actions import SearchJourneys
from flights.core.handlers import SearchJourneysHandler
from flights.core.repositories import JourneysRepository


class FlightsCommandBus:
    def __init__(self, bus: dict[Any, Any]):
        self._commands = {}
        for action, handler in bus.items():
            self._commands[action] = handler

    def handle(self, action) -> Any:
        return self._commands[action]()


class FlightsContainer(DeclarativeContainer):
    wiring_config = WiringConfiguration(modules=[
        'flights.api.models',
        'flights.api.repositories',
        'flights.api.views',
    ])
    config = Configuration()
    journeys_repository: Factory[JourneysRepository] = Factory(
        JourneysRepository,
        provider_base_url=config.journeys_provider_base_url,
        endpoint=config.journeys_provider_endpoint_v1,
    )
    command_bus: Factory[FlightsCommandBus] = Factory(
        FlightsCommandBus,
        {
            SearchJourneys: Factory(
                SearchJourneysHandler,
                journeys_repository=journeys_repository,
            )
        }
    )
