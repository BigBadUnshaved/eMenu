# syntax=docker/dockerfile:1
FROM python:3.6
ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/emenu
RUN apt-get -y update
RUN apt-get -y install libpq-dev
RUN apt-get -y install python3-dev
COPY requirements.txt /usr/src/emenu/
RUN pip install -r requirements.txt
COPY . /usr/src/emenu/
