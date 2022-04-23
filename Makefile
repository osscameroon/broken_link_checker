.DEFAULT_GOAL=help

CONFIG_FILE=./conf.ini
VENVPATH=blc_venv
PYTHON=$(VENVPATH)/bin/python3

venv: $(VENVPATH)/bin/activate
$(VENVPATH)/bin/activate: requirements.txt
	test -d $(VENVPATH) || virtualenv -p python3 $(VENVPATH); \
	. $(VENVPATH)/bin/activate; \
	pip install -r requirements.txt

$(CONFIG_FILE):
	echo "[-] adding config file..."
	cp example.conf.ini $(CONFIG_FILE)

##install-deps: setup your dev environment
install-deps: venv $(CONFIG_FILE)

##run: run the api locally - ex: make run link="https://osscameroon.com"
run: install-deps
	$(PYTHON) -m broken_link_checker $(link) --delay 1

lint: install-deps venv
	$(PYTHON) -m flake8 broken_link_checker --show-source --statistics

build: install-deps
	$(PYTHON) -m build

##test: test your code
test: build
	$(PYTHON) -m unittest
	$(PIP) install dist/blc-*.whl
	PYTHON=$(PYTHON) NB_BROKEN_LINK_EXPECTED=22 sh tests/checker_test.sh
	PYTHON=$(PYTHON) NB_BROKEN_LINK_EXPECTED=28 BLC_FLAGS="-D -n" sh tests/checker_test.sh

clean:
	rm -rf $(VENVPATH) dist

##help: show help
help: Makefile
	@sed -n 's/^##//p' $<

.PHONY: help venv install-deps test lint