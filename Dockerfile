FROM python:3.8.6-buster

COPY api.py /api.py
COPY LexAI /LexAI
COPY requirements.txt /requirements.txt

RUN echo “deb [trusted=yes] https://apt.fury.io/meilisearch/ /” > /etc/apt/sources.list.d/fury.list
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

CMD uvicorn api:app --host 0.0.0.0 --port $PORT
