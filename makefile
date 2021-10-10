install: install-mongodb install-python3


install-mongodb:
	echo "hello world"


install-python3:
	sudo apt install python3-pip
	python3 -m venv venv
	. venv/bin/activate
	pip3 install -r requirements.txt


run:
	python3 src/main.py