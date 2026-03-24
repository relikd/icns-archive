
help:
	@echo available: analyze, zip

analyze:
	./analyze.py ../icon-archive/ ../results/extracted.db 2>> ../results/extracted-error.log

zip:
	@find ../icon-archive/ -name '.DS_Store' -type f -delete -print
	@echo 'find all "_src.txt" files ...'
	@find ../icon-archive/ -name _src.txt -execdir sh -c 'echo "$$PWD.zip"; ls | sort -n | zip "../$$(basename "$$PWD").zip" -q -@' \;
