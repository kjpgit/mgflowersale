.PHONY: build test

build:
	./sale.py < template.html > index.html

test:
	nohup python -m SimpleHTTPServer 8002 &
