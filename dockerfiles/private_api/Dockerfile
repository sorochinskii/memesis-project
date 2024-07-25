FROM python:3.11

WORKDIR /code
COPY source/private_api/requirements.txt .

RUN pip install -r requirements.txt

ADD source/private_api .
