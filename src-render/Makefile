
help:
	@echo available:
	@echo crop, crop-cleanup, collage, collage-cleanup, analyze

crop:
	@for x in ../rendered-archive/*/; do \
		if [ -e "$$x/app/png/256.png" ]; then \
			echo "processing $$x"; \
			./postprocess-crop.py "$$x"; \
		fi \
	done

crop-cleanup:
	@echo 'This will delete all original screenshots.'
	@echo 'Are you sure? [y/N] ' && read ans && [ $${ans:-N} = y ]
	find ../rendered-archive/ -type f -path '*/app/*/*' -name '*.png' -not -name '*.crop.png' -not -name '*.collage.png' -delete

collage:
	@for x in ../rendered-archive/*/; do \
		if [ -e "$$x/app/png/256.crop.png" ]; then \
			echo "processing $$x"; \
			./postprocess-collage.py "$$x/app/"; \
		fi \
	done

collage-cleanup:
	@echo 'This will delete all cropped images.'
	@echo 'Are you sure? [y/N] ' && read ans && [ $${ans:-N} = y ]
	@for x in ../rendered-archive/*/app/*/; do \
		if [ -f "$${x%/}.collage.png" ]; then \
			rm -rf "$$x"; \
		fi \
	done

analyze:
	./analyze.py ../rendered-archive/ ../results/rendered.db
