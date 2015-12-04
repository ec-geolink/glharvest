.PHONY: clean

all: clean sync

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

sync:
	rm -r d1lod
	cp -R ~/src/d1lod/d1lod/ d1lod
	
docs: FORCE
	cd docs && $(MAKE)

FORCE:
