.DEFAULT_GOAL=help

CONFIG_FILE=./conf.ini
VENVPATH=blc_venv
PYTHON=$(VENVPATH)/bin/python3
PIP=$(VENVPATH)/bin/pip

venv: $(VENVPATH)/bin/activate
$(VENVPATH)/bin/activate: requirements.txt
	test -d $(VENVPATH) || python3 -m venv $(VENVPATH); \
	. $(VENVPATH)/bin/activate; \
	$(PIP) install -r requirements.txt

$(CONFIG_FILE):
	echo "[-] adding config file..."
	cp example.conf.ini $(CONFIG_FILE)

##install-deps: setup your dev environment
install-deps: venv $(CONFIG_FILE)

##run: run the api locally - ex: make run link="https://osscameroon.com"
run: install-deps
	$(PYTHON) -m blc $(link) --delay 1

lint: install-deps
	$(PYTHON) -m flake8 blc --show-source --statistics

build: install-deps
	$(PYTHON) -m build

##test: test your code
test: build
	$(PYTHON) -m unittest
	ls dist/blc-*.whl | sort -r | grep . -m 1 > /tmp/last_package
	$(PIP) install -r /tmp/last_package
	PYTHON=$(PYTHON) NB_BROKEN_LINK_EXPECTED=23 sh tests/checker_test.sh
	PYTHON=$(PYTHON) NB_BROKEN_LINK_EXPECTED=31 BLC_FLAGS="-n" sh tests/checker_test.sh
	PYTHON=$(PYTHON) NB_BROKEN_LINK_EXPECTED=31 BLC_FLAGS="-n -b 5" sh tests/checker_test.sh

clean:
	rm -rf $(VENVPATH) dist

##help: show help
help: Makefile
	@sed -n 's/^##//p' $<

.PHONY: help venv install-deps test lint
