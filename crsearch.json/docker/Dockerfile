FROM python:3.6.2-alpine3.6

MAINTAINER melpon <shigemasa7watanabe+docker@gmail.com>

COPY requirements.txt .

RUN set -ex \
  && apk add --no-cache bash \
  && pip install -r requirements.txt
