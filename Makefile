SRC_DIR=.
TESTS_DIR=tests
PACKAGE_DIR=telegram_webapp_auth
REFERENCES_DIR=docs/references

mypy:
	poetry run mypy --config formatters-cfg.toml $(SRC_DIR)

flake:
	poetry run flake8 --toml-config formatters-cfg.toml $(SRC_DIR)

black:
	poetry run black --config formatters-cfg.toml $(SRC_DIR)

black-lint:
	poetry run black --check --config formatters-cfg.toml $(SRC_DIR)

isort:
	poetry run isort --settings-path formatters-cfg.toml $(SRC_DIR)

doc-lint:
	poetry run lazydocs --validate --output-path $(REFERENCES_DIR) $(PACKAGE_DIR)

format: black isort doc-lint

lint: flake mypy black-lint

cov:
	poetry run pytest --cov=$(PACKAGE_DIR) $(SRC_DIR)

lock:
	poetry lock --no-update

install:
	poetry install --no-root

mkdocs-serve:
	poetry run mkdocs serve

mkdocs-deploy:
	poetry run mkdocs gh-deploy --force

test:
	poetry run pytest -n 2 $(TESTS_DIR)
