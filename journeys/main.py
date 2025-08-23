import logging

from fastapi import FastAPI, Request

from journeys.app import views
from journeys.containers import JourneysContainer

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(name)s:\nMessage: %(message)s\nProps=%(props)s",
)
logger = logging.getLogger('journeys-app')


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(views.router)
    container = JourneysContainer()
    container.config.flights_provider_base_url.from_env('FLIGHTS_PROVIDER_BASE_URL')
    container.config.flights_provider_endpoint_v1.from_env('FLIGHTS_PROVIDER_ENDPOINT_V1')
    container.config.cache_uri.from_env('CACHE_URI')
    container.config.cache_key.from_env('CACHE_KEY')
    app.container = container
    return app


app = create_app()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    response = await call_next(request)

    log_data = {
        'request': {
            'method': request.method,
            'url': str(request.url),
        },
        'response': {
            'status_code': response.status_code,
            'body': body.decode('utf-8') if body else None,
        }
    }
    logger.info('Request processed.', extra={'props': log_data})

    return response

