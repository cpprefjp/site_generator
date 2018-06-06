#!/bin/bash

function show_help() {
  echo "$0 build"
  echo "$0 run"
  echo "$0 test"
  echo "$0 console"
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
    docker build -t cpprefjp/site_generator-crsearch docker ;;
  "run" )
    docker run $DOCKER_RM -v `pwd`:/var/src $DOCKER_IT cpprefjp/site_generator-crsearch /bin/bash -c 'cd /var/src && python run.py' ;;
  "test" )
    docker run $DOCKER_RM -v `pwd`:/var/src $DOCKER_IT cpprefjp/site_generator-crsearch /bin/bash -c 'cd /var/src && python -m unittest' ;;
  "console" )
    docker run $DOCKER_RM -v `pwd`:/var/src $DOCKER_IT cpprefjp/site_generator-crsearch /bin/bash -c 'cd /var/src; exec /bin/bash' ;;
  * )
    show_help
    exit 1 ;;
esac
