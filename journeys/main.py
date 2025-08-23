from fastapi import FastAPI

from journeys.app import views
from journeys.containers import JourneysContainer


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(views.router)
    container = JourneysContainer()
    container.config.journeys_provider_base_url.from_env('JOURNEYS_PROVIDER_BASE_URL')
    container.config.journeys_provider_endpoint_v1.from_env('JOURNEYS_PROVIDER_ENDPOINT_V1')
    container.config.cache_uri.from_env('CACHE_URI')
    container.config.cache_key.from_env('CACHE_KEY')
    app.container = container
    return app


app = create_app()
