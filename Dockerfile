FROM python:3.8.5-slim-buster

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY stardog ./stardog
COPY stardog_server.py ./

CMD python stardog_server.py
