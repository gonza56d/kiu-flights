from datetime import datetime, date
from http import HTTPStatus
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from journeys.containers import JourneysCommandBus
from journeys.core.models import Journey, FlightEvent
from journeys.main import app

client = TestClient(app)


class TestSearchJourneysApp:
    """Test endpoint behavior."""

    @patch.object(JourneysCommandBus, 'handle')
    def test_search_journeys_responses_two_journeys_found(self, mock_handle):
        mock_handle.return_value = [
            Journey(
                flight_events=[
                    FlightEvent(
                        flight_number='XX1234',
                        from_='BUE',
                        to='SAO',
                        departure_time=datetime(2025, 7, 1, 13),
                        arrival_time=datetime(2025, 7, 1, 17),
                    ),
                ],
            ),
            Journey(
                flight_events=[
                    FlightEvent(
                        flight_number='XX5678',
                        from_='BUE',
                        to='MON',
                        departure_time=datetime(2025, 7, 1, 13),
                        arrival_time=datetime(2025, 7, 1, 14),
                    ),
                    FlightEvent(
                        flight_number='XX9012',
                        from_='MON',
                        to='SAO',
                        departure_time=datetime(2025, 7, 1, 15),
                        arrival_time=datetime(2025, 7, 1, 17, 30),
                    ),
                ],
            )
        ]

        response = client.get(
            '/journeys/search',
            params={
                'date': date(2025, 7, 1),
                'origin': 'BUE',
                'destination': 'SAO',
            }
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == [
            {
                'connections': 0,
                'path': [
                    {
                        'flight_number': 'XX1234',
                        'from': 'BUE',
                        'to': 'SAO',
                        'departure_time': '2025-07-01T13:00:00',
                        'arrival_time': '2025-07-01T17:00:00',
                    },
                ],
            },
            {
                'connections': 1,
                'path': [
                    {
                        'flight_number': 'XX5678',
                        'from': 'BUE',
                        'to': 'MON',
                        'departure_time': '2025-07-01T13:00:00',
                        'arrival_time': '2025-07-01T14:00:00',
                    },
                    {
                        'flight_number': 'XX9012',
                        'from': 'MON',
                        'to': 'SAO',
                        'departure_time': '2025-07-01T15:00:00',
                        'arrival_time': '2025-07-01T17:30:00',
                    },
                ],
            },
        ]

    @patch.object(JourneysCommandBus, 'handle')
    def test_search_journeys_responses_no_journey_found(self, mock_handle):
        mock_handle.return_value = []

        response = client.get(
            '/journeys/search',
            params={
                'date': date(2025, 7, 1),
                'origin': 'BUE',
                'destination': 'SAO',
            }
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == []

    @patch.object(JourneysCommandBus, 'handle')
    def test_search_journeys_responses_internal_server_error(self, mock_handle):
        mock_handle.side_effect = Exception('MOCKED_INTERNAL_SERVER_ERROR')

        with pytest.raises(Exception):
            client.get(
                '/journeys/search',
                params={
                    'date': date(2025, 7, 1),
                    'origin': 'BUE',
                    'destination': 'SAO',
                }
            )

    @patch.object(JourneysCommandBus, 'handle')
    def test_search_journeys_responses_bad_request(self, mock_handle):
        mock_handle.return_value = []

        response = client.get(
            '/journeys/search',
            params={
                'date': None,
                'origin': 'BUE',
                'destination': 'SAO',
            }
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
