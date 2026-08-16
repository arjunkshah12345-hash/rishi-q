# Makefile — common RISHI-Q commands

.PHONY: status reproduce reproduce-all visuals flagship validate-freeze test ci-local graphs

status:
	uv run rishiq-isef status

reproduce:
	uv run rishiq-isef reproduce --config configs/isef2027.yaml

reproduce-all:
	uv run rishiq-isef reproduce-all --config configs/isef2027.yaml

visuals:
	@open visuals/isef2027/index.html 2>/dev/null || xdg-open visuals/isef2027/index.html 2>/dev/null || echo "Open visuals/isef2027/index.html"

flagship:
	uv run python scripts/run_isef_akasa_sound_field.py
	uv run python scripts/make_isef_extra_figures.py
	uv run python scripts/run_isef_expansion_v2.py

validate-freeze:
	uv run python scripts/validate_isef2027_freeze.py

graphs:
	uv run rishiq-isef graphs

test:
	uv run pytest -q

ci-local: test validate-freeze
	uv run rishiq-isef confirmatory-status | grep -q LOCKED
	@echo "ci-local OK"
