build:
	docker compose build

up:
	docker compose run --rm --service-ports api

test:
	docker compose run --rm --service-ports api pytest -vvv tests/

test-single:
	docker compose run --rm --service-ports api pytest -vvv tests/ -k $(TEST)
