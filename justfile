set shell := ["zsh", "-cu"]

gen:
    uv run python -m dhlkit._gen

gen-check:
    uv run python -m dhlkit._gen --check

lint:
    uv run ruff check .
    uv run ruff format --check .

format:
    uv run ruff check --fix .
    uv run ruff format .

typecheck:
    uv run ty check src tests

test:
    uv run pytest -m "not live"

live:
    uv run pytest -m live -v

check: gen-check lint typecheck test
