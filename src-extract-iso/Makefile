
help:
	@echo available: analyze, zip

analyze:
	./analyze.py ../collection-extracted/ ../results/extracted.db 2>> ../results/extracted-error.log

zip:
	@find ../collection-extracted/ -name '.DS_Store' -type f -delete -print
	@echo 'find all "_src.txt" files ...'
	@find ../collection-extracted/ -name _src.txt -execdir sh -c 'echo "$$PWD.zip"; ls | sort -n | zip "../$$(basename "$$PWD").zip" -q -@' \;
