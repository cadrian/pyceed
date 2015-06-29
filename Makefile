FILES=$(shell find src -name "*.py")
TESTS=$(shell find test/unit -name "test*.py")
TESTS_FLAG=$(shell find test/unit -name "test*.py" | sed 's/\.py$$/.flag/g')

all: test

test: $(TESTS_FLAG)

dep:
	install-deps.sh

%.flag: %.py $(FILES)
	PYTHONPATH=$(shell pwd)/src:$(PYTHONPATH) python3 $< && touch $@

clean:
	rm -f $(TESTS_FLAG)
	$(shell find . -name __pycache__ -exec rm -rf {} +)

run-update: $(FILES)
	PYTHONPATH=$(shell pwd)/src:$(PYTHONPATH) python3 src/pyceed/update_feeds.py

run-server: $(FILES)
	PYTHONPATH=$(shell pwd)/src:$(PYTHONPATH) python3 src/pyceed/serve_feeds.py

.PHONY: all test dep run-update run-server
