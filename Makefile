.DEFAULT_GOAL=help

CONFIG_FILE=./conf.ini

# uv automatically manages .venv/
VENVPATH=.venv
PYTHON=uv run python
UV=uv

$(CONFIG_FILE):
	@echo "[-] adding config file..."
	cp example.conf.ini $(CONFIG_FILE)

##install-deps: setup your dev environment
install-deps: $(CONFIG_FILE)
	which uv || curl -LsSf https://astral.sh/uv/0.12.23/install.sh | sh
	$(UV) lock
	$(UV) sync

##run: run the api locally - ex: make run link="https://osscameroon.com"
run: install-deps
	$(UV) run blc $(link) --delay 1

##lint: run ruff
lint: install-deps
	$(UV) tool run ruff format blc --check
	$(UV) tool run ruff check blc

##build: build wheel & sdist using hatchling through uv
build: install-deps
	$(UV) build

## run unitest with pytest
test: install-deps
	$(UV) run pytest

##test: run unit tests, install built wheel, run shell tests
shell-test: build
	ls dist/*.whl | sort -r | head -n1 > /tmp/last_package
	$(UV) pip install -r /tmp/last_package
	PYTHON="uv run python" NB_BROKEN_LINK_EXPECTED=23 sh tests/checker_test.sh


##clean: remove build artifacts
clean:
	rm -rf .venv dist uv.lock

##help: show help
help: Makefile
	@sed -n 's/^##//p' $<

.PHONY: help install-deps test lint build run clean
