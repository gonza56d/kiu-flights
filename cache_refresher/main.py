from os import environ
from time import sleep

from flights.api.repositories import JourneysHTTPRepository

from cache_refresher.cache import RedisCacheRepository
from cache_refresher.cache_refresher import CacheRefresher


def main():
    cache_refresh_every = environ.get('CACHE_REFRESH_EVERY', 0)
    if not cache_refresh_every:
        return
    cache_refresher = CacheRefresher(
        journey_repository=JourneysHTTPRepository(
            provider_base_url=environ.get('JOURNEYS_PROVIDER_BASE_URL', ''),
            endpoint=environ.get('JOURNEYS_PROVIDER_ENDPOINT_V1', ''),
        ),
        cache_repository=RedisCacheRepository(
            repository_uri=environ.get('CACHE_URI', ''),
            cache_key=environ.get('CACHE_KEY', ''),
        ),
    )
    while True:
        cache_refresher.run()
        sleep(int(cache_refresh_every))


if __name__ == '__main__':
    main()
