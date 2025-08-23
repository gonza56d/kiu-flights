"""Declarative IoC layer."""
from os import environ
from typing import Any

from dependency_injector.containers import DeclarativeContainer, WiringConfiguration
from dependency_injector.providers import Configuration, Factory

from flights.app.repositories import JourneysHTTPRepository, JourneysCacheRepository
from flights.core.actions import SearchJourneys
from flights.core.handlers import SearchJourneysHandler
from flights.core.repositories import JourneysRepository


class FlightsCommandBus:
    """
    A lightweight command bus for dispatching actions to their handlers.

    This bus maps action types to corresponding handler factories. When an
    action is handled, the bus instantiates the appropriate handler and
    invokes it with the given action.

    Attributes:
        _commands (dict[str, Any]): A registry mapping action class names to handler factories.
    """

    _commands: dict[str, Any] = {}

    def __init__(self, bus: dict[Any, Any]):
        for action, handler in bus.items():
            FlightsCommandBus._commands[action.provides.__name__] = handler

    def handle(self, action) -> Any:
        """
        Dispatch an action to its corresponding handler.

        Args:
            action (Any): The action instance to be processed.

        Returns:
            Any: The result of executing the action’s handler.
        """
        command = FlightsCommandBus._commands[action.__class__.__name__]()
        return command(action)


class FlightsContainer(DeclarativeContainer):
    """
    Dependency injection container for the Flights service.

    This container wires together modules, repositories, actions, and
    handlers required by the Flights domain. It provides configuration
    and factories for external services and the command bus.

    Attributes:
        config (Configuration): Holds service configuration parameters.
        journeys_repository (Factory[JourneysRepository]): Factory for
            creating a journeys repository backed by an HTTP provider.
        command_bus (Factory[FlightsCommandBus]): Factory for the command bus,
            mapping actions to their handlers.
    """
    wiring_config = WiringConfiguration(modules=[
        'flights.app.models',
        'flights.app.repositories',
        'flights.app.views',
    ])
    config = Configuration()

    use_cache = bool(int(environ.get('CACHE_REFRESH_EVERY', 0)))
    journeys_repository: Factory[JourneysRepository] = Factory(
        JourneysCacheRepository,
        repository_uri=config.cache_uri,
        cache_key=config.cache_key,
    ) if use_cache else Factory(
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
