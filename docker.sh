#!/bin/bash

function show_help() {
  echo "$0 build"
  echo "$0 run <run.py args>"
  echo "$0 coding"
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
    docker build -t cpprefjp/site_generator docker ;;
  "run" )
    if [ $# -lt 2 ]; then
      show_help
      exit 1
    fi
    docker run -v `pwd`:/var/src -it cpprefjp/site_generator /bin/bash -c "cd /var/src && ./run.py $*" ;;
  "coding" )
    docker run -v `pwd`:/var/src -it cpprefjp/site_generator /bin/bash -c "cd /var/src && flake8 `find . -name '*.py'`" ;;
  "console" )
    docker run -v `pwd`:/var/src -it cpprefjp/site_generator /bin/bash -c "cd /var/src && exec /bin/bash" ;;
  * )
    show_help
    exit 1 ;;
esac
