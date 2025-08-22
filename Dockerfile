FROM python:3.12.3

ENV PYTHONUNBUFFERED=1
WORKDIR /flights

COPY . .
COPY requirements.txt .
COPY .env .

RUN pip install -r requirements.txt
