FROM python:3.8.6-buster

COPY api.py /api.py
COPY LexAI /LexAI
COPY requirements.txt /requirements.txt
COPY twitter_credentials.json /twitter_credentials.json

RUN echo "deb [trusted=yes] https://apt.fury.io/meilisearch/ /" > /etc/apt/sources.list.d/fury.list
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

