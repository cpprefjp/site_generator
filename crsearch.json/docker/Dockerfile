FROM python:3.7.2-alpine3.8

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

COPY requirements.txt .

RUN set -ex \
  && apk add --no-cache bash \
  && pip install -r requirements.txt

WORKDIR /var/src
