from typing import Callable
import logging

from fastapi import Request, Response
from fastapi.routing import APIRoute

LOG_FORMAT = (
    "%(levelname)s:%(name)s:%(message)s "
    "request=%(request)s response=%(response)s"
)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
LOGGER = logging.getLogger(__name__)


class JourneysRouteHandler(APIRoute):
    """Custom route handler to normalize error responses and log processed requests and responses."""

    def get_route_handler(self) -> Callable:
        """
        Intercept all calls to an endpoint.

        Add standard logs for requests and responses.
        Add standard error message responses.
        """
        original_route_handler = super().get_route_handler()

        async def journeys_route_handler(request: Request) -> Response:
            LOGGER.info(
                'Processing request.',
                {'request': {'method': request.method, 'url': request.url}},
            )
            response = await original_route_handler(request)
            LOGGER.info(
                'Successfully processed request and response.',
                {
                    'request': {'method': request.method, 'url': request.url},
                    'response': {'status_code': response.status_code, 'body': response.body},
                },
            )
            return response

        return journeys_route_handler
