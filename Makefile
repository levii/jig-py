package_name = jig-py

export PATH := venv/bin:$(shell echo ${PATH})

.PHONY: setup
setup:
	[ -d venv ] || python3 -m venv venv
	pip3 install twine wheel pytest pip-tools
	#pip3 install -r requirements.txt

.PHONY: release
release: clean build
	python -m twine upload \
		--repository-url https://upload.pypi.org/legacy/ \
		dist/*

.PHONY: build
build: clean
	python setup.py sdist bdist_wheel

.PHONY: clean
clean:
	rm -rf $(subst -,_,${package_name}).egg-info dist build

.PHONY: mypy
mypy:
	${server_runner} mypy jig/

.PHONY: black
black:
	${server_runner} black jig/ tests/

.PHONY: flake8
flake8:
	${server_runner} flake8 jig/ tests/

.PHONY: check
check: mypy black flake8
