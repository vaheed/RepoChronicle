.PHONY: install lint format-check typecheck test check compose-config up down logs

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

format-check:
	ruff format --check .

typecheck:
	mypy src

test:
	pytest -q

check: lint format-check typecheck test

compose-config:
	docker compose config --quiet

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=200
