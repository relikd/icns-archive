
help:
	@echo 'available:'
	@echo '  clean, build, export'
	@echo '  crop, crop-cleanup, collage, collage-cleanup'
	@echo '  analyze'

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
	@for x in ../collection-rendered/*/; do \
		if [ -e "$$x/app/png/256.png" ]; then \
			echo "processing $$x"; \
			./postprocess-crop.py "$$x"; \
		fi \
	done
	@for x in ../collection-rendered-edge-cases/*/; do \
		if [ -e "$$x/app/alpha-bits.png" ]; then \
			echo "processing $$x"; \
			./postprocess-crop.py "$$x"; \
		fi \
	done

crop-cleanup:
	@echo 'This will delete all original screenshots.'
	@echo 'Are you sure? [y/N] ' && read ans && [ $${ans:-N} = y ]
	find ../collection-rendered/ -type f -path '*/app/*/*' -name '*.png' -not -name '*.crop.png' -not -name '*.collage.png' -delete
	find ../collection-rendered-edge-cases/ -type f -path '*/app/*' -name '*.png' -not -name '*.crop.png' -delete

collage:
	@for x in ../collection-rendered/*/; do \
		if [ -e "$$x/app/png/256.crop.png" ]; then \
			echo "processing $$x"; \
			./postprocess-collage.py "$$x/app/"; \
		fi \
	done

collage-cleanup:
	@echo 'This will delete all cropped images.'
	@echo 'Are you sure? [y/N] ' && read ans && [ $${ans:-N} = y ]
	@for x in ../collection-rendered/*/app/*/; do \
		if [ -f "$${x%/}.collage.png" ]; then \
			rm -rf "$$x"; \
		fi \
	done

# Part 3: analyze results

analyze:
	./analyze.py ../collection-rendered/ ../results/rendered.db
