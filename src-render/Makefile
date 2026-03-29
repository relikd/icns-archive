
help:
	@echo 'available: clean, build, export, crop, collage, analyze'

# Part 1: generate icons

clean:
	rm -rf build export tmp out

build: gen-variants.py
	rm -rf build
	./gen-variants.py build

export/variants.zip: build ./render-icons ./assets/
	mkdir -p export
	ln -s build/variants input
	zip -o export/variants.zip --symlinks -r render-icons assets/dsstore-* input/*
	rm input

export/edge-cases.zip: build ./render-icons ./assets/
	mkdir -p export
	ln -s build/edge-cases input
	zip -o export/edge-cases.zip --symlinks -r render-icons assets/dsstore-* input/*
	rm input

.PHONY: export
export: export/variants.zip export/edge-cases.zip
	@echo 'Delete build dir? [Y/n] ' && read ans && [ $${ans:-y} = y ]
	rm -rf build

# Part 2: postprocess rendered icons

crop:
	./postprocess-crop.py ..

collage:
	./postprocess-collage.py ..

# Part 3: analyze results

analyze:
	./analyze.py ../collection-rendered/ ../results/rendered.db
