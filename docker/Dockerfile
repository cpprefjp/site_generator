FROM python:2.7.14-alpine3.6

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

COPY requirements.txt .

RUN set -ex \
  && apk add --no-cache \
    bash \
    gcc \
    git \
    musl-dev

RUN set -ex \
  && pip install -r requirements.txt

WORKDIR /var/src
