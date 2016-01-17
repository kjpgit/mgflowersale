.PHONY: build test sync

build:
	./src/generate.py
	./src/images.py | sort -g

sync:
	curl "https://docs.google.com/spreadsheets/d/1CfSFMJ838WgaG-P_byEEynmp8Rzu7ECGR1ZVee7HH20/pub?gid=1553865443&single=true&output=csv" > src/data.csv

test:
	nohup python -m SimpleHTTPServer 8002 &
