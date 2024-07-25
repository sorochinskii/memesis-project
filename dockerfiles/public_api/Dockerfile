FROM python:3.11

WORKDIR /code
COPY source/public_api/requirements.txt .

RUN pip install -r requirements.txt

ADD source/public_api .
