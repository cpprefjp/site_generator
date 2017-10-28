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

case "$1" in
  "build" )
    docker build -t cpprefjp/site_generator-crsearch docker ;;
  "run" )
    docker run -v `pwd`:/var/src -it cpprefjp/site_generator-crsearch /bin/bash -c 'cd /var/src && python run.py' ;;
  "test" )
    docker run -v `pwd`:/var/src -it cpprefjp/site_generator-crsearch /bin/bash -c 'cd /var/src && python -m unittest' ;;
  "console" )
    docker run -v `pwd`:/var/src -it cpprefjp/site_generator-crsearch /bin/bash -c 'cd /var/src; exec /bin/bash' ;;
  * )
    show_help
    exit 1 ;;
esac
