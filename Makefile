# Connect to cockroach db
ADDR ?= cockroachdb://root@localhost:26257/company_sqlalchemy?sslmode=disable

.PHONY: start
start:
	ADDR=$(ADDR) ./server.py --port=6543

.PHONY: deps
deps:
	# To avoid permissions errors, the following should be run in a virtualenv
	# (preferred) or as root.
	pip install flask-sqlalchemy cockroachdb