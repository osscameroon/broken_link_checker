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
	$(UV) lock
	$(UV) sync

##run: run the api locally - ex: make run link="https://osscameroon.com"
run: install-deps
	$(UV) run blc $(link) --delay 1

##lint: run flake8
lint: install-deps
	$(UV) run flake8 blc --show-source --statistics

##build: build wheel & sdist using hatchling through uv
build: install-deps
	$(UV) build

## run unitest with pytest
test: 
	$(UV) run pytest

##test: run unit tests, install built wheel, run shell tests
shell-test: build
	ls dist/*.whl | sort -r | head -n1 > /tmp/last_package
	$(UV) pip install -r /tmp/last_package
	PYTHON="uv run python" NB_BROKEN_LINK_EXPECTED=23 sh tests/checker_test.sh


##clean: remove build artifacts
clean:
	rm -rf .venv dist

##help: show help
help: Makefile
	@sed -n 's/^##//p' $<

.PHONY: help install-deps test lint build run clean
