#!/bin/bash

function show_help() {
  echo "$0 build"
  echo "$0 run <run.py args>"
  echo "$0 coding"
  echo "$0 console"
  echo "$0 localhost cpprefjp"
  echo "$0 localhost boostjp"
}

if [ $# -lt 1 ]; then
  show_help
  exit 1
fi

set -e

cd "`dirname $0`"

if [ -z "$DOCKER_IT" ] && [ "${DOCKER_IT:-A}" = "${DOCKER_IT-A}" ]; then
  DOCKER_IT="-it"
fi

DOCKER_RM=${DOCKER_RM---rm}

case "$1" in
  "build" )
    docker build -t cpprefjp/site_generator docker ;;
  "run" )
    if [ $# -lt 2 ]; then
      show_help
      exit 1
    fi
    shift 1
    docker run $DOCKER_RM -v `pwd`:/var/src cpprefjp/site_generator ./run.py "$@" ;;
  "coding" )
    docker run $DOCKER_RM -v `pwd`:/var/src cpprefjp/site_generator flake8 *.py markdown_to_html/*.py ;;
  "console" )
    docker run $DOCKER_RM -v `pwd`:/var/src $DOCKER_IT cpprefjp/site_generator /bin/bash ;;
  "localhost" )
    if [ $# -lt 2 ]; then
      show_help
      exit 1
    fi
    cd $2/$2.github.io
    docker run $DOCKER_RM -v `pwd`:/var/src -p 8000:8000 cpprefjp/site_generator python -m http.server 8000 ;;
  * )
    show_help
    exit 1 ;;
esac
