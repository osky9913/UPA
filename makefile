BIN=venv/bin/
.ONESHELL:

install: install-mongodb install-python3 install-env

install-mongodb:
	sudo apt install -y mongodb;
	sudo systemctl restart mongodb;
	sudo systemctl status mongodb;


install-python3:
	sudo apt install python3-pip
	sudo apt install python3.8-venv
	python3 -m venv venv

install-env:
	( . venv/bin/activate; pip install -r requirements.txt; )

run:
	$(BIN)python3 src/main.py

csv:
	$(BIN)python3 src/extract.py

plot:
	$(BIN)python3 src/plot.py

update-lib:
	python -m pip freeze > requirements.txt

install-lib:
	pip3 install -r requirements.txt

clean-data:
	rm -rf data/*.csv

clean-env:
	rm -rf venv

clean: clean-data clean-env