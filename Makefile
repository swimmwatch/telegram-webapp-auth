SRC_DIR=.
PACKAGE_DIR=telegram_webapp_auth

mypy:
	poetry run mypy $(SRC_DIR)

flake:
	poetry run flake8 $(SRC_DIR)

black:
	poetry run black $(SRC_DIR)

lint: flake mypy

test:
	poetry run pytest $(SRC_DIR)

cov:
	poetry run pytest --cov=$(PACKAGE_DIR) $(SRC_DIR)
