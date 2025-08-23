import logging
import sys
from os import environ
from time import sleep

from journeys.app.repositories import FlightsHTTPRepository

from cache_refresher.cache import RedisCacheRepository
from cache_refresher.cache_refresher import CacheRefresher

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(name)s",
)
LOGGER = logging.getLogger('cache-refresher')


def main():
    LOGGER.info("Evaluating if cache_refresher should run.")
    cache_refresh_every = environ.get('CACHE_REFRESH_EVERY', 0)
    if not cache_refresh_every:
        LOGGER.info("Cache refresher disabled.")
        sys.exit(0)
    LOGGER.info("Cache refresher enabled.")
    cache_refresher = CacheRefresher(
        flights_repository=FlightsHTTPRepository(
            provider_base_url=environ.get('FLIGHTS_PROVIDER_BASE_URL', ''),
            endpoint=environ.get('FLIGHTS_PROVIDER_ENDPOINT_V1', ''),
        ),
        cache_repository=RedisCacheRepository(
            repository_uri=environ.get('CACHE_URI', ''),
            cache_key=environ.get('CACHE_KEY', ''),
        ),
    )
    while True:
        LOGGER.debug("Running cache_refresher.")
        cache_refresher.run()
        LOGGER.debug("Cache refreshed.")
        sleep(int(cache_refresh_every))


if __name__ == '__main__':
    main()
