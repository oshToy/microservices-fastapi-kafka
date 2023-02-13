FROM python:3.8-slim

WORKDIR /app

RUN apt-get update
RUN apt install -y \
gcc g++ python-dev librocksdb-dev build-essential \
libsnappy-dev zlib1g-dev libbz2-dev libgflags-dev \
liblz4-dev libzstd-dev curl

COPY ./requirements.txt /requirements.txt

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

COPY ./$API_NAME /app
COPY ./core /app/core

ENV HOST 127.0.0.1
ENV PORT 8007
CMD uvicorn main:app --reload --host $HOST --port $PORT
