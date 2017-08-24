#!/bin/bash

./build.sh
docker run -v `pwd`:/var/src -it cpprefjp/crsearch /bin/sh -c 'cd /var/src; python -m unittest'
