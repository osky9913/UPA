BIN=venv/bin/
install: install-mongodb install-python3git p


install-mongodb:
	sudo apt install -y mongodb;
	sudo systemctl restart mongodb;
	sudo systemctl status mongodb;


install-python3:
	sudo apt install python3-pip
	python3 -m venv venv
	. venv/bin/activate
	pip3 install -r requirements.txt



activate:
	source ./venv/bin/activate



run:
	$(BIN)python3 src/main.py

update-lib:
	python -m pip freeze > requirements.txt

install-lib:
	pip3 install -r requirements.txt