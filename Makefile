SRC_DIR=.
PACKAGE_DIR=telegram_webapp_auth
SPEC_DIR=docs/spec

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
	poetry run lazydocs --validate --output-path $(SPEC_DIR) $(PACKAGE_DIR)

format: black isort doc-lint

lint: flake mypy black-lint

test:
	poetry run pytest $(SRC_DIR)

cov:
	poetry run pytest --cov=$(PACKAGE_DIR) $(SRC_DIR)

lock:
	poetry lock --no-update
