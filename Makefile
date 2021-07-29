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
add_tweets_pp:
	@python LexAI/database.py build_ms_many indices=twitter_press,twitter_politicians
	@python LexAI/database.py export_json indices=twitter_press,twitter_politicians

add_tweets_query:
	@python LexAI/database.py build_ms_many indices=twitter_query
	@python LexAI/database.py export_json indices=twitter_query

add_regulations:
	@python LexAI/database.py build_ms_many indices=eurlex,consultations
	@python LexAI/database.py export_json indices=eurlex,consultations

update_consul_displayed_att:
	@python LexAI/database.py update_consul_displayed_att

update_sentiments:
	@python LexAI/analyse.py get_all_sentiments

add_all:
	@python LexAI/database.py build_ms_many

export_json:
	@python LexAI/database.py export_json

import_json:
	@python LexAI/database.py import_json

import_json_replace:
	@python LexAI/database.py import_json replace=True

update_entries:
	@python LexAI/database.py import_updates
	@python LexAI/database.py import_data index=twitter_politicians
	@python LexAI/database.py import_data index=twitter_press

# ----------------------------------
#      API
# ----------------------------------
run_api:
	@curl -L https://install.meilisearch.com | sh
	@./meilisearch& uvicorn api:app --reload  # load web server with code autoreload


# ----------------------------------
#         HEROKU COMMANDS
# ----------------------------------

streamlit:
	-@streamlit run app.py

heroku_login:
	-@heroku login

heroku_create_app:
	-@heroku create ${APP_NAME}

deploy_heroku:
	-@git push heroku master
	-@heroku ps:scale web=1
# ----------------------------------
#         TESTS
# ----------------------------------
say_hello:
	-@echo "Hello World"