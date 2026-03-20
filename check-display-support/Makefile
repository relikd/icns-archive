
help:
	@echo available: verify, crop, crop-cleanup

verify:
	@for x in ../rendered-archive/*/; do \
		if [ ! -e "$$x/analysis.md" ] || [ ! -s "$$x/analysis.md" ]; then \
			echo "processing $$x"; \
			./verify.py "$$x" > "$$x/analysis.md"; \
		fi \
	done

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
	find ../rendered-archive/ -type f -path '*/app/*' -name '*.png' -not -name '*.crop.png' -delete
