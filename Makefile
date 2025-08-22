build:
	docker compose build

up:
	docker compose up -d cache_refresher && \
	docker compose run --rm --service-ports app

test:
	docker compose run --rm --service-ports app pytest -vvv tests/

test-single:
	docker compose run --rm --service-ports app pytest -vvv tests/ -k $(TEST)