install:
	@poetry init --no-interaction --name=fly-in
	@poetry add --dev flake8
	@poetry add --dev mypy
	@echo "\n\033[0;31m¡ATENTION! Run: make run MAP=<src/maps.txt>.\033[0m"

run:
	@poetry run python3 main.py $(MAP)

debug:
	poetry run python3 -m pdb main.py

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "\033[0;31mCache removed\033[0m"


fclean: clean
	@rm -rf .venv
	@rm -rf .mypy_cache
	@rm -f poetry.lock
	@rm -f pyproject.toml
	@echo "\033[0;31mVirtual environment and cache removed\033[0m"

reinstall: fclean init

lint:
	@poetry run flake8 . --exclude=.venv,venv,__pycache__,.mypy_cache
	@poetry run mypy . \
		--explicit-package-bases \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	@echo "\033[0;31mVirtual environment and cache removed\033[0m"
	@poetry run flake8 . --exclude=.venv,venv,__pycache__,.mypy_cache
	@poetry run mypy . \
		--strict 
		--explicit-package-bases