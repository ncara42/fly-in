PYTHON = poetry run python
MAP = maps/example_map.txt

.PHONY: install run lint clean

install:
	poetry install

run:
	$(PYTHON) main.py $(MAP)

lint:
	poetry run flake8 .
	poetry run mypy .

clean:
	rm -rf `find . -name __pycache__`
	rm -rf .mypy_cache