from dataclasses import dataclass
from datetime import timedelta

from journeys.core.actions import SearchJourneys
from journeys.core.models import Journey, FlightEvent
from journeys.core.repositories import FlightsRepository


@dataclass
class SearchJourneysHandler:

    flights_repository: FlightsRepository

    def __call__(self, action: SearchJourneys) -> list[Journey]:
        journeys: list[Journey] = []
        flight_events = self.flights_repository.get_flight_events()

        for flight_event in flight_events:
            flight_event.mask_flight_number()
            if flight_event.matches_from_and_time(action.from_, action.date):
                if flight_event.to == action.to:  # direct fly case
                    journeys.append(Journey(flight_events=[flight_event]))
                else:   # search possible connections
                    available_connections: list[FlightEvent] = self.__search_connections(
                        action=action,
                        initial_flight_event=flight_event,
                        flight_events=flight_events,
                    )
                    for connection in available_connections:
                        connection.mask_flight_number()
                        journeys.append(Journey(flight_events=[flight_event, connection]))

        return journeys

    @staticmethod
    def __search_connections(
            action: SearchJourneys,
            initial_flight_event: FlightEvent,
            flight_events: list[FlightEvent],
    ) -> list[FlightEvent]:
        """
        Search possible connections for a given flight event.

        Given a SearchJourneys action, filter for a given starting flight event, all other flight events that match
        connection in location and time.
        Max connections is 1. Waiting time from initial flight event arrival time until connection departure time
        cannot be more than 4 hours. Total flight duration from initial flight event departure time until connection
        arrival time cannot be more than 24 hours.

        :param action: SearchJourneys action, input filter.
        :param initial_flight_event: flight event to search all possible connections for.
        :param flight_events: all the flight events to filter if possible connections for initial_flight_event.
        :return: list of flight events that match conditions to be a connection.
        """
        return list(
            filter(
                lambda connection: (
                    connection.from_ == initial_flight_event.to and connection.to == action.to
                    and (
                        timedelta(hours=0, minutes=0, seconds=0) <=
                        connection.departure_time - initial_flight_event.arrival_time <= timedelta(hours=4)
                    )
                    and connection.arrival_time - initial_flight_event.departure_time <= timedelta(hours=24)
                ),
                flight_events
            )
        )
