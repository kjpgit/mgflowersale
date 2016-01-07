.PHONY: build test sync

build:
	./sale.py < template.html > index.html


sync:
	curl "https://docs.google.com/spreadsheets/d/1CfSFMJ838WgaG-P_byEEynmp8Rzu7ECGR1ZVee7HH20/pub?gid=1553865443&single=true&output=csv" > data.txt

test:
	nohup python -m SimpleHTTPServer 8002 &
