# ALS SubZero Root Makefile
# Developed by Samin Sami (ALS = Al Sami).

PYTHON ?= python

.PHONY: all test bench demo clean c package

all: test

c:
	$(MAKE) -C src/c

test:
	PYTHONPATH=src $(PYTHON) tests/run_all.py

bench:
	PYTHONPATH=src $(PYTHON) scripts/run_benchmark.py

demo:
	PYTHONPATH=src $(PYTHON) scripts/run_demo.py

package:
	PYTHONPATH=src $(PYTHON) scripts/package_release.py

clean:
	$(MAKE) -C src/c clean || true
	rm -rf __pycache__ src/**/__pycache__ tests/__pycache__ .pytest_cache *.zip
