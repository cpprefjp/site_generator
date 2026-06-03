FROM python:3.12-alpine

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

RUN \
  git config --global --add safe.directory /var/src && \
  git config --global --add safe.directory /var/src/kunai && \
  git config --global --add safe.directory /var/src/cpprefjp/site && \
  git config --global --add safe.directory /var/src/boostjp/site && \
  :


WORKDIR /var/src
