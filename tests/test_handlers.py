from datetime import datetime, date
from unittest.mock import MagicMock

from flights.core.actions import SearchJourneys
from flights.core.handlers import SearchJourneysHandler
from flights.core.models import FlightEvent, Journey


class TestSearchJourneysHandler:

    def setup_method(self) -> None:
        self.handler = SearchJourneysHandler(journeys_repository=MagicMock())

    def test_no_flights_available(self):
        # Given no available flight events at the moment.
        self.handler.journeys_repository.get_flight_events.return_value = []
        # When any search is performed.
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='MAD',
                date_=date(2024, 9, 9)
            )
        )
        # Then the results shows an empty list
        assert search_journeys_result == []

    def test_one_flight_without_connections(self):
        """
        Happy path test case.

        Most straight forward finding one flight event without connections.
        """
        # Given existing travel from Buenos Aires to Madrid that has a 12-hour duration.
        existing_flying_events = [
            FlightEvent(
                flight_number='IB1234',
                from_='BUE',
                to='MAD',
                departure_time=datetime(2021, 12, 31, 23, 59),
                arrival_time=datetime(2022, 1, 1, 12),
            )
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search is from Buenos Aires to Madrid for the given departure date is made
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='MAD',
                date_=date(2021, 12, 31)
            )
        )

        # Then the results shows the given flight event with no connections
        assert search_journeys_result == [
            Journey(
                flight_events=[
                    FlightEvent(
                        flight_number='XX1234',
                        from_='BUE',
                        to='MAD',
                        departure_time=datetime(2021, 12, 31, 23, 59),
                        arrival_time=datetime(2022, 1, 1, 12),
                    ),
                ]
            )
        ]
        for journey in search_journeys_result:
            assert journey.connections == len(journey.flight_events) - 1 if journey.flight_events else 0

    def test_two_flights_one_connection(self):
        """
        Happy path test case.

        Second most straight forward finding two flight events resulting in one connection.
        """
        # Given existing flights from Buenos Aires to Madrid
        # and from Madrid to Paris, that have less than 4 hours waiting and
        # less than 24 hours of duration in total.
        existing_flying_events = [
            FlightEvent(
                flight_number='IB1234',
                from_='BUE',
                to='MAD',
                departure_time=datetime(2021, 12, 31, 23),
                arrival_time=datetime(2022, 1, 1, 12),
            ),
            FlightEvent(
                flight_number='IB5678',
                from_='MAD',
                to='PAR',
                departure_time=datetime(2022, 1, 1, 14),
                arrival_time=datetime(2022, 1, 1, 16),
            ),
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search for travel from Buenos Aires to Paris in the same departure time is made.
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='PAR',
                date_=date(2021, 12, 31)
            )
        )

        # Then the status code is 200 and the json response shows one connection with the two flights
        assert search_journeys_result == [
            Journey(
                flight_events=[
                    FlightEvent(
                        flight_number='XX1234',
                        from_='BUE',
                        to='MAD',
                        departure_time=datetime(2021, 12, 31, 23),
                        arrival_time=datetime(2022, 1, 1, 12),
                    ),
                    FlightEvent(
                        flight_number='XX5678',
                        from_='MAD',
                        to='PAR',
                        departure_time=datetime(2022, 1, 1, 14),
                        arrival_time=datetime(2022, 1, 1, 16),
                    ),
                ]
            )
        ]
        for journey in search_journeys_result:
            assert journey.connections == len(journey.flight_events) - 1 if journey.flight_events else 0

    def test_more_than_two_flight_events_limit(self):
        """
        Non-happy path.

        Handle case where there are more than two flight events for the required travel.
        """
        # Given three existing flight events that have less than 4 waiting hours between connections
        # and less than 24-hour duration in total.
        existing_flying_events = [
            FlightEvent(
                flight_number='IB1234',
                from_='BUE',
                to='MAD',
                departure_time=datetime(2021, 12, 31, 23),
                arrival_time=datetime(2022, 1, 1, 12),
            ),
            FlightEvent(
                flight_number='IB5678',
                from_='MAD',
                to='PAR',
                departure_time=datetime(2022, 1, 1, 14),
                arrival_time=datetime(2022, 1, 1, 16),
            ),
            FlightEvent(
                flight_number='IB9012',
                from_='PAR',
                to='ROM',
                departure_time=datetime(2022, 1, 1, 17),
                arrival_time=datetime(2022, 1, 1, 19),
            ),
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search for travel from Buenos Aires to Paris in the same departure time is made.
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='ROM',
                date_=date(2021, 12, 31)
            )
        )

        # Then the result don't have any journey
        assert search_journeys_result == []

    def test_more_than_4_hour_connection_wait_limit(self):
        """
        Non-happy path.

        Handle case where the waiting time in one of the connections is more than 4 hours.
        """
        # Given existing flight events that have more than 4-hour waiting between connection.
        existing_flying_events = [
            FlightEvent(
                flight_number='IB1234',
                from_='BUE',
                to='MAD',
                departure_time=datetime(2021, 12, 31, 23),
                arrival_time=datetime(2022, 1, 1, 12),
            ),
            FlightEvent(
                flight_number='IB5678',
                from_='MAD',
                to='PAR',
                departure_time=datetime(2022, 1, 1, 18),
                arrival_time=datetime(2022, 1, 1, 20),
            ),
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search that matches cities and time is made
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='PAR',
                date_=date(2021, 12, 31)
            )
        )

        # Then the result don't have any journey
        assert search_journeys_result == []

    def test_more_than_24_hour_travel_limit(self):
        """
        Non-happy path.

        Handle case where the number of flight events and waiting time are ok, but
        the total duration of the travel is more than 24 hours.
        """
        # Given two existing flight events that in total last more than 24 hours
        existing_flying_events = [
            FlightEvent(
                flight_number='IB1234',
                from_='BUE',
                to='MAD',
                departure_time=datetime(2021, 12, 31, 23),
                arrival_time=datetime(2022, 1, 1, 12),
            ),
            FlightEvent(
                flight_number='IB5678',
                from_='MAD',
                to='TOK',
                departure_time=datetime(2022, 1, 1, 16),
                arrival_time=datetime(2022, 1, 2, 1),
            ),
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search that matches cities and time is made
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='TOK',
                date_=date(2021, 12, 31)
            )
        )

        # Then the result don't have any journey
        assert search_journeys_result == []

    def test_one_connection_between_many_flight_events(self):
        """
        Complex happy path test case.

        There are two flight events with one connection matching the search between many other
        flight events.
        """
        # Given two existing flight events that can make a connection
        # between many other unrelated flight events.
        existing_flying_events = [
            FlightEvent(
                flight_number='IB1234',
                from_='BUE',
                to='MAD',
                departure_time=datetime(2021, 12, 31, 23),
                arrival_time=datetime(2022, 1, 1, 12),
            ),
            FlightEvent(
                flight_number='IB5678',
                from_='MAD',
                to='BER',
                departure_time=datetime(2022, 1, 1, 13),
                arrival_time=datetime(2022, 1, 1, 15),
            ),
            FlightEvent(
                flight_number='IB9012',
                from_='MAD',
                to='PAR',
                departure_time=datetime(2022, 1, 1, 13),
                arrival_time=datetime(2022, 1, 1, 15),
            ),
            FlightEvent(
                flight_number='IB3456',
                from_='BER',
                to='MAD',
                departure_time=datetime(2022, 1, 1, 12, 30),
                arrival_time=datetime(2022, 1, 1, 15),
            ),
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search that matches cities and time is made
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='BER',
                date_=date(2021, 12, 31)
            )
        )

        # Then the result don't have any journey
        assert search_journeys_result == [
            Journey(
                flight_events=[
                    FlightEvent(
                        flight_number='XX1234',
                        from_='BUE',
                        to='MAD',
                        departure_time=datetime(2021, 12, 31, 23),
                        arrival_time=datetime(2022, 1, 1, 12),
                    ),
                    FlightEvent(
                        flight_number='XX5678',
                        from_='MAD',
                        to='BER',
                        departure_time=datetime(2022, 1, 1, 13),
                        arrival_time=datetime(2022, 1, 1, 15),
                    ),
                ]
            )
        ]
        for journey in search_journeys_result:
            assert journey.connections == len(journey.flight_events) - 1 if journey.flight_events else 0

    def test_no_results(self):
        """
        Non-happy path.

        Simply there are no flights that match the search.
        """
        # Given many flights existing
        existing_flying_events = [
            FlightEvent(
                flight_number='IB5678',
                from_='MAD',
                to='BER',
                departure_time=datetime(2022, 1, 1, 13),
                arrival_time=datetime(2022, 1, 1, 15),
            ),
            FlightEvent(
                flight_number='IB9012',
                from_='MAD',
                to='PAR',
                departure_time=datetime(2022, 1, 1, 13),
                arrival_time=datetime(2022, 1, 1, 15),
            ),
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search that doesn't match any departure city
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='BER',
                date_=date(2022, 1, 1)
            )
        )

        # Then a result with no journeys is returned
        assert search_journeys_result == []

    def test_more_than_one_possible_travel_path(self):
        """
        Complex happy path test case.

        There are two different possible travel paths between all the results.
        """
        # Given many existing flight events and two have the same departure and destination city,
        # one with one scale and the other direct.
        existing_flying_events = [
            FlightEvent(
                flight_number='IB1234',
                from_='BUE',
                to='MAD',
                departure_time=datetime(2022, 1, 1, 1),
                arrival_time=datetime(2022, 1, 1, 12),
            ),
            FlightEvent(
                flight_number='IB5678',
                from_='MAD',
                to='BER',
                departure_time=datetime(2022, 1, 1, 14),
                arrival_time=datetime(2022, 1, 1, 15, 30),
            ),
            FlightEvent(
                flight_number='IB9012',
                from_='BUE',
                to='BER',
                departure_time=datetime(2022, 1, 1, 0, 30),
                arrival_time=datetime(2022, 1, 1, 12),
            ),
            FlightEvent(
                flight_number='IB3456',
                from_='PAR',
                to='BER',
                departure_time=datetime(2022, 1, 1, 12, 30),
                arrival_time=datetime(2022, 1, 1, 15),
            ),
        ]
        self.handler.journeys_repository.get_flight_events.return_value = existing_flying_events

        # When a search that doesn't match any departure city
        search_journeys_result = self.handler(
            SearchJourneys(
                from_='BUE',
                to='BER',
                date_=date(2022, 1, 1)
            )
        )

        # Then the result shows two possible journeys, one with one scale and the other direct
        assert search_journeys_result == [
            Journey(
                flight_events=[
                    FlightEvent(
                        flight_number='XX1234',
                        from_='BUE',
                        to='MAD',
                        departure_time=datetime(2022, 1, 1, 1),
                        arrival_time=datetime(2022, 1, 1, 12),
                    ),
                    FlightEvent(
                        flight_number='XX5678',
                        from_='MAD',
                        to='BER',
                        departure_time=datetime(2022, 1, 1, 14),
                        arrival_time=datetime(2022, 1, 1, 15, 30),
                    ),
                ]
            ),
            Journey(
                flight_events=[
                    FlightEvent(
                        flight_number='XX9012',
                        from_='BUE',
                        to='BER',
                        departure_time=datetime(2022, 1, 1, 0, 30),
                        arrival_time=datetime(2022, 1, 1, 12),
                    ),
                ]
            )
        ]
        for journey in search_journeys_result:
            assert journey.connections == len(journey.flight_events) - 1 if journey.flight_events else 0
