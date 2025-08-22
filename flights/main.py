from fastapi import FastAPI

from flights.api import views
from flights.containers import FlightsContainer


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(views.router)
    container = FlightsContainer()
    container.config.journeys_provider_base_url.from_env('JOURNEYS_PROVIDER_BASE_URL')
    container.config.journeys_provider_endpoint_v1.from_env('JOURNEYS_PROVIDER_ENDPOINT_V1')
    app.container = container
    return app


app = create_app()
