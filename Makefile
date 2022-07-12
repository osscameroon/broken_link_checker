.DEFAULT_GOAL=help

VENVPATH=venv
PYTHON=$(VENVPATH)/bin/python3
PIP=$(VENVPATH)/bin/pip

venv: $(VENVPATH)/bin/activate
$(VENVPATH)/bin/activate: requirements.txt
	test -d $(VENVPATH) || python3 -m venv $(VENVPATH); \
	. $(VENVPATH)/bin/activate; \
	$(PIP) install -r requirements.txt

##install-deps: setup your dev environment
install-deps: venv

##run: run the api locally - ex: make run link="https://osscameroon.com"
run: install-deps
	$(PYTHON) -m blc $(link)

lint: install-deps
	$(PYTHON) -m flake8 blc --show-source --statistics

build: install-deps
	$(PYTHON) -m build

##test: test your code
test: build

clean:
	rm -rf $(VENVPATH) dist

##help: show help
help: Makefile
	@sed -n 's/^##//p' $<

.PHONY: help venv install-deps test lint
