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

format: black isort

lint: flake mypy black-lint

lock:
	poetry lock

install:
	poetry install --no-root

mkdocs-serve:
	poetry run mkdocs serve

mkdocs-deploy:
	poetry run mkdocs gh-deploy --force

test:
	poetry run pytest --benchmark-autosave --cov=$(PACKAGE_DIR) --cov-branch --cov-report=xml --numprocesses logical $(TESTS_DIR)

actionlint:
	docker run --rm -v $(pwd):/repo --workdir /repo rhysd/actionlint:latest -color
