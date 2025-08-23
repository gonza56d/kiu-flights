# kiu-flights 🌎

Kiu Journeys is a Python-based application designed to facilitate the exploration and management of flight data. Utilizing modern development practices, it offers a robust solution for users seeking to analyze and interact with flight information efficiently.

## How To Run 🚀

1. Prerequisites: Docker, docker compose, python 3.8+.
2. Clone the repository: `git clone https://github.com/gonza56d/kiu-journeys.git`
3. CD into the repo: `cd kiu-journeys`
4. Set up environment variables: `cp .env.copy .env` 
5. Build the application: `make build`
6. Run tests: `make test`
7. Run the application: `make up`
8. (Optional) Play with the cache: You can disable it by setting `CACHE_REFRESH_EVERY=0` in `.env`, or enabling warm cache to refresh every x seconds by setting any number greater than 0.

## Repository Structure 📂
#### In this repo, you will find three main python packages:

- `journeys` -> Core implementation of the solution.
- `cache_refresher` -> Warm cache service. Enable or disable via .env (CACHE_REFRESH_EVERY). Refresh interval is set in seconds. 
- `tests` -> Unit tests for business logic (tests/test_handlers.py) and API tests (tests/test_app.py). 

## Technical Details 🔧

- **Architecture:** `journeys` works in a three-layer architecture: `views -> handlers -> repositories`.
- **SOLID principles:** IoC with dependency injection and a Command Bus are implemented in [containers.py](https://github.com/gonza56d/kiu-journeys/blob/master/journeys/containers.py).
- **Abstract repositories:** The flights provider (mock API) and Redis cache both implement the same abstract class, FlightsRepository, allowing easy swapping of implementations without touching core business logic.
- **API layer:** FastAPI is used for HTTP endpoints. Concrete implementations are in journeys/app/, while journeys/core/ contains framework-agnostic business logic.

## Going The Extra Mile 🚀

- **Warm cache (cache_refresher):** reduces response times from ~650ms to ~20ms when enabled, improving concurrency.
- **Dynamic repository injection:** At startup, the app checks CACHE_REFRESH_EVERY. It injects either:

    - **Redis warm cache repository** if caching is enabled, or
    - **HTTP flights provider** if caching is disabled.

  Both follow the same contract, so the core business logic remains unchanged regardless of the source.

## Final Thoughts 👨🏻‍💻

*This solution strictly follows SOLID principles, ensuring scalability, maintainability, and easy substitution of different flight providers. At the same time, I understand that some of these patterns are not always the most common in the Python community, and I am fully capable of adapting to a team’s preferred practices when needed.*