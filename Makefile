SRC_DIR=.
PACKAGE_DIR=telegram_webapp_auth
SPEC_DIR=docs/spec

mypy:
	poetry run mypy $(SRC_DIR)

flake:
	poetry run flake8 $(SRC_DIR)

black:
	poetry run black $(SRC_DIR)

doc-lint:
	poetry run lazydocs --validate --output-path $(SPEC_DIR) $(PACKAGE_DIR)

lint: flake mypy doc-lint

test:
	poetry run pytest $(SRC_DIR)

cov:
	poetry run pytest --cov=$(PACKAGE_DIR) $(SRC_DIR)
