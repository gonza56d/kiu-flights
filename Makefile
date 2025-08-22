build:
	docker compose build

up:
	docker compose run --rm --service-ports app

test:
	docker compose run --rm --service-ports app pytest -vvv tests/

test-single:
	docker compose run --rm --service-ports app pytest -vvv tests/ -k $(TEST)
