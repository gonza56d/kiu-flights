from datetime import date
import pytest
from http import HTTPStatus
from pytest_httpx import HTTPXMock


@pytest.mark.asyncio
class TestApi:

    async def test_search_journeys_success__one_flight_no_connections(
        self,
        async_client,
        httpx_mock: HTTPXMock,
    ):
        """
        Happy path test case.

        Most straight forward finding one flight event without connections.
        """
        # Given an existing travel from Buenos Aires to Madrid
        # that has 12-hour duration.
        provider_api_response = [
            {
                'flight_number': 'IB1234',
                'departure_city': 'BUE',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-31T23:59:59.000Z',
                'arrival_datetime': '2022-01-01T12:00:00.000Z'
            }
        ]
        httpx_mock.add_response(
            method='GET',
            url='https://mock.apidog.com/m1/814105-793312-default/flight-events',
            status_code=HTTPStatus.OK,
            json=provider_api_response,
        )
        expected_search_journeys_response = [
            {
                'connections': 0,
                'path': [
                    {
                        'flight_number': 'XX1234',
                        'from': 'BUE',
                        'to': 'MAD',
                        'departure_time': '2021-12-31 23:59',
                        'arrival_time': '2022-01-01 12:00'
                    }
                ]
            }
        ]

        # When a request from Buenos Aires to Madrid for the given departure date is made
        search_journeys_response = await async_client.get(
            '/journeys/search',
            params={
                'from': 'BUE',
                'to': 'MAD',
                'date': date(2021, 12, 31).isoformat(),
            },
        )

        # Then the status code is 200 and the json shows the given flight event with no connections
        assert search_journeys_response.status_code == HTTPStatus.OK
        assert search_journeys_response.json() == expected_search_journeys_response

    async def test_search_journeys_success__two_flights_one_connection(
        self,
        async_client,
        httpx_mock: HTTPXMock,
    ):
        """
        Happy path test case.

        Second most straight forward finding two flight events resulting in one connection.
        """
        # Given existing flights from Buenos Aires to Madrid
        # and from Madrid to Paris, that have less than 4 hours waiting and
        # less than 24 hours of duration in total.
        provider_api_response = [
            {
                'flight_number': 'IB1234',
                'departure_city': 'BUE',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-31T23:59:59.000Z',
                'arrival_datetime': '2022-01-01T12:00:00.000Z'
            },
            {
                'flight_number': 'IB5678',
                'departure_city': 'MAD',
                'arrival_city': 'PAR',
                'departure_datetime': '2022-01-01T14:00:00.000Z',
                'arrival_datetime': '2022-01-01T16:00:00.000Z'
            },
        ]
        httpx_mock.add_response(
            method='GET',
            url='https://mock.apidog.com/m1/814105-793312-default/flight-events',
            status_code=HTTPStatus.OK,
            json=provider_api_response,
        )
        expected_search_journeys_response = [
            {
                'connections': 1,
                'path': [
                    {
                        'flight_number': 'XX5678',
                        'from': 'BUE',
                        'to': 'MAD',
                        'departure_time': '2021-12-31 23:59',
                        'arrival_time': '2022-01-01 12:00'
                    },
                    {
                        'flight_number': 'XX5678',
                        'departure_city': 'MAD',
                        'arrival_city': 'PAR',
                        'departure_datetime': '2022-01-01 14:00',
                        'arrival_datetime': '2022-01-01 16:00'
                    }
                ]
            }
        ]

        # When a request to search for a travel from Buenos Aires to Paris in the
        # same departure time is made.
        search_journeys_response = await async_client.get(
            '/journeys/search',
            params={
                'from': 'BUE',
                'to': 'PAR',
                'date': date(2021, 12, 31).isoformat(),
            },
        )

        # Then the status code is 200 and the json response shows one connection with the two flights
        assert search_journeys_response.status_code == HTTPStatus.OK
        assert search_journeys_response.json() == expected_search_journeys_response

    async def test_search_journeys_no_results__more_than_two_flight_events_limit(
        self,
        async_client,
        httpx_mock: HTTPXMock,
    ):
        """
        Non-happy path.

        Handle case where there are more than two flight events for the required travel.
        """
        # Given three existing flight events that have less than 4 waiting hours between connections
        # and less than 24-hour duration in total.
        provider_api_response = [
            {
                'flight_number': 'IB1234',
                'departure_city': 'BUE',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-31T23:59:59.000Z',
                'arrival_datetime': '2022-01-01T12:00:00.000Z'
            },
            {
                'flight_number': 'IB5678',
                'departure_city': 'MAD',
                'arrival_city': 'PAR',
                'departure_datetime': '2022-01-01T14:00:00.000Z',
                'arrival_datetime': '2022-01-01T16:00:00.000Z'
            },
            {
                'flight_number': 'IB9012',
                'departure_city': 'PAR',
                'arrival_city': 'ROM',
                'departure_datetime': '2022-01-01T17:00:00.000Z',
                'arrival_datetime': '2022-01-01T19:00:00.000Z'
            },
        ]
        httpx_mock.add_response(
            method='GET',
            url='https://mock.apidog.com/m1/814105-793312-default/flight-events',
            status_code=HTTPStatus.OK,
            json=provider_api_response,
        )

        # When a request from first existing travel event departure city (Buenos Aires) and same departure time,
        # to last arrival city (Rome) is made.
        search_journeys_response = await async_client.get(
            '/journeys/search',
            params={
                'from': 'BUE',
                'to': 'ROM',
                'date': date(2021, 12, 31).isoformat(),
            },
        )

        # Then a response status code 200 with empty results is returned.
        assert search_journeys_response.status_code == HTTPStatus.OK
        assert search_journeys_response.json() == []

    async def test_search_journeys_no_results__more_than_4_hour_connection_wait_limit(
        self,
        async_client,
        httpx_mock: HTTPXMock,
    ):
        """
        Non-happy path.

        Handle case where the waiting time in one of the conections is more than 4 hours.
        """
        # Given existing flight events that have more than 4-hour waiting between connection.
        provider_api_response = [
            {
                'flight_number': 'IB1234',
                'departure_city': 'BUE',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-31T23:59:59.000Z',
                'arrival_datetime': '2022-01-01T12:00:00.000Z'
            },
            {
                'flight_number': 'IB5678',
                'departure_city': 'MAD',
                'arrival_city': 'PAR',
                'departure_datetime': '2022-01-01T18:00:00.000Z',
                'arrival_datetime': '2022-01-01T20:00:00.000Z'
            },
        ]
        httpx_mock.add_response(
            method='GET',
            url='https://mock.apidog.com/m1/814105-793312-default/flight-events',
            status_code=HTTPStatus.OK,
            json=provider_api_response,
        )

        # When a request from the first flight event departure city (Buenos Aires)
        # and same departure time is made
        search_journeys_response = await async_client.get(
            '/journeys/search',
            params={
                'from': 'BUE',
                'to': 'PAR',
                'date': date(2021, 12, 31).isoformat(),
            },
        )

        # Then a status code 200 with empty results is returned
        assert search_journeys_response.status_code == HTTPStatus.OK
        assert search_journeys_response.json() == []

    async def test_search_journeys_no_results__more_than_24_hour_travel_limit(
        self,
        async_client,
        httpx_mock: HTTPXMock,
    ):
        """
        Non-happy path.

        Handle case where the number of flight events and waiting time are ok, but
        the total duration of the travel is more than 24 hours.
        """
        # Given two existing flight events that in total last more than 24 hours
        provider_api_response = [
            {
                'flight_number': 'IB1234',
                'departure_city': 'BUE',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-31T23:59:59.000Z',
                'arrival_datetime': '2022-01-01T12:00:00.000Z'
            },
            {
                'flight_number': 'IB5678',
                'departure_city': 'MAD',
                'arrival_city': 'TOK',
                'departure_datetime': '2022-01-01T16:00:00.000Z',
                'arrival_datetime': '2022-01-02T01:00:00.000Z'
            },
        ]
        httpx_mock.add_response(
            method='GET',
            url='https://mock.apidog.com/m1/814105-793312-default/flight-events',
            status_code=HTTPStatus.OK,
            json=provider_api_response,
        )

        # When a request to travel from Buenos Aires at the same departure time,
        # to Tokyo is made
        search_journeys_response = await async_client.get(
            '/journeys/search',
            params={
                'from': 'BUE',
                'to': 'TOK',
                'date': date(2021, 12, 31).isoformat(),
            },
        )

        # Then the response is a 200 status code with empty results
        assert search_journeys_response.status_code == HTTPStatus.OK
        assert search_journeys_response.json() == []

    async def test_search_journeys_success__complex_case_one_connection_between_many_flight_events(
        self,
        async_client,
        httpx_mock: HTTPXMock,
    ):
        """
        Complex happy path test case.

        There are two flight events with one connection matching the search between many other
        flight events.
        """
        # Given two existing flight events that can make a connection
        # between many other unrelated flight events.
        provider_api_response = [
            {
                'flight_number': 'IB1234',
                'departure_city': 'BUE',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-31T23:59:59.000Z',
                'arrival_datetime': '2022-01-01T12:00:00.000Z'
            },
            {
                'flight_number': 'IB5678',
                'departure_city': 'MAD',
                'arrival_city': 'BER',
                'departure_datetime': '2021-12-01T13:00:00.000Z',
                'arrival_datetime': '2022-01-01T15:00:00.000Z'
            },
            {
                'flight_number': 'IB9012',
                'departure_city': 'MAD',
                'arrival_city': 'PAR',
                'departure_datetime': '2021-12-01T13:00:00.000Z',
                'arrival_datetime': '2022-01-01T15:00:00.000Z'
            },
            {
                'flight_number': 'IB9012',
                'departure_city': 'BER',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-01T12:30:00.000Z',
                'arrival_datetime': '2022-01-01T15:00:00.000Z'
            }
        ]
        httpx_mock.add_response(
            method='GET',
            url='https://mock.apidog.com/m1/814105-793312-default/flight-events',
            status_code=HTTPStatus.OK,
            json=provider_api_response,
        )
        expected_search_journeys_response = [
            {
                'connections': 1,
                'path': [
                    {
                        'flight_number': 'XX1234',
                        'from': 'BUE',
                        'to': 'MAD',
                        'departure_datetime': '2021-12-31 23:59',
                        'arrival_datetime': '2022-01-01 12:00'
                    },
                    {
                        'flight_number': 'XX5678',
                        'from': 'MAD',
                        'to': 'BER',
                        'departure_datetime': '2021-12-01 13:00',
                        'arrival_datetime': '2022-01-01 15:00'
                    },
                ]
            }
        ]

        # When a request from Buenos Aires to Berlin for the given departure date is made
        search_journeys_response = await async_client.get(
            '/journeys/search',
            params={
                'from': 'BUE',
                'to': 'MAD',
                'date': date(2021, 12, 31).isoformat(),
            },
        )

        # Then the status code is 200 and the json shows the given flight events with one connection
        assert search_journeys_response.status_code == HTTPStatus.OK
        assert search_journeys_response.json() == expected_search_journeys_response

    async def test_search_journeys_no_results(
        self,
        async_client,
        httpx_mock: HTTPXMock,
    ):
        """
        Non-happy path.

        Simply there are no flights for the request.
        """
        # Given many flights existing
        provider_api_response = [
            {
                'flight_number': 'IB1234',
                'departure_city': 'BUE',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-31T23:59:59.000Z',
                'arrival_datetime': '2022-01-01T12:00:00.000Z'
            },
            {
                'flight_number': 'IB5678',
                'departure_city': 'MAD',
                'arrival_city': 'BER',
                'departure_datetime': '2021-12-01T13:00:00.000Z',
                'arrival_datetime': '2022-01-01T15:00:00.000Z'
            },
            {
                'flight_number': 'IB9012',
                'departure_city': 'MAD',
                'arrival_city': 'PAR',
                'departure_datetime': '2021-12-01T13:00:00.000Z',
                'arrival_datetime': '2022-01-01T15:00:00.000Z'
            },
            {
                'flight_number': 'IB9012',
                'departure_city': 'BER',
                'arrival_city': 'MAD',
                'departure_datetime': '2021-12-01T12:30:00.000Z',
                'arrival_datetime': '2022-01-01T15:00:00.000Z'
            }
        ]
        httpx_mock.add_response(
            method='GET',
            url='https://mock.apidog.com/m1/814105-793312-default/flight-events',
            status_code=HTTPStatus.OK,
            json=provider_api_response,
        )

        # When a search request for a travel event that does not exist at the moment is made.
        search_journeys_response = await async_client.get(
            '/journeys/search',
            params={
                'from': 'BUE',
                'to': 'LON',
                'date': date(2021, 12, 31).isoformat(),
            },
        )

        # Then the status code is 200 and the json shows empty results
        assert search_journeys_response.status_code == HTTPStatus.OK
        assert search_journeys_response.json() == []
