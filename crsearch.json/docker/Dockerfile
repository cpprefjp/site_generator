FROM python:3.8.2-alpine

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

COPY requirements.txt .

RUN set -ex \
  && apk add --no-cache bash \
  && pip install -r requirements.txt

WORKDIR /var/src
