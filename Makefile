PIPENV_VENV_IN_PROJECT=1
export PIPENV_VENV_IN_PROJECT

SCRAPPER_DIR := ./scrapper
COMPOSE_PARAMS := -f docker/docker-compose.yaml 

black:
	pipenv run black $(SCRAPPER_DIR)

devinstall:
	pipenv install --dev

docker-build:
	docker-compose $(COMPOSE_PARAMS) build

docker-run:
	docker-compose $(COMPOSE_PARAMS) up

lint:
	pipenv run flake8 $(SCRAPPER_DIR)

localrun:
	pipenv run python -m scrapper

run:
	pipenv run python -m scrapper

tests:
	pipenv run pytest