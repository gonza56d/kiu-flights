FROM python:3.12.3

ENV PYTHONUNBUFFERED=1
WORKDIR /journeys

COPY . .
COPY requirements.txt .
COPY .env .

RUN pip install -r requirements.txt
