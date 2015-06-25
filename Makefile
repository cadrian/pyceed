FILES=$(shell find src -name "*.py")
TESTS=$(shell find test/unit -name "*.py")

all: test

test: $(FILES) $(TESTS)
	PYTHONPATH=$(shell pwd)/src:$(PYTHONPATH) python3 -m unittest discover -s $(shell pwd)/test/unit

.PHONY: all test
