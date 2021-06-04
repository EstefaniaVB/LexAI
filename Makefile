# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
install_requirements:
	@pip install -r requirements.txt
	@pip3 install meilisearch

check_code:
	@flake8 scripts/* LexAI/*.py

black:
	@black scripts/* LexAI/*.py

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"

ftest:
	@Write me

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr LexAI-*.dist-info
	@rm -fr LexAI.egg-info

install:
	@pip install . -U
	@pip install -r requirements.txt
	@curl -L https://install.meilisearch.com | sh

all: clean install test black check_code

count_lines:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./scripts -name '*-*' -exec  wc -l {} \; | sort -n| awk \
		        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./tests -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

# ----------------------------------
#      UPLOAD PACKAGE TO PYPI
# ----------------------------------
PYPI_USERNAME=<AUTHOR>
build:
	@python setup.py sdist bdist_wheel

pypi_test:
	@twine upload -r testpypi dist/* -u $(PYPI_USERNAME)

pypi:
	@twine upload dist/* -u $(PYPI_USERNAME)


# ----------------------------------
#      Manage DB
# ----------------------------------
build_ms:
	@echo "IMPORTANT: run ./meilisearch in seperate terminal"
	@python LexAI/dbsearch.py build_ms_many

export_json:
	@echo "IMPORTANT: run ./meilisearch in seperate terminal"
	@python LexAI/dbsearch.py export_json

import_json:
	@echo "IMPORTANT: run ./meilisearch in seperate terminal"
	@python LexAI/dbsearch.py import_json

# ----------------------------------
#      API
# ----------------------------------
run_api:
	@./meilisearch& uvicorn api:app --reload  # load web server with code autoreload

