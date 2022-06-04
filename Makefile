
install-virtualenv:
	rm -rf ./local.virtualenv
	virtualenv -p python3.6 local.virtualenv
	./local.virtualenv/bin/pip install -U pip
	./local.virtualenv/bin/pip install -r requirements.txt


test:
	./local.virtualenv/bin/pytest --cov
