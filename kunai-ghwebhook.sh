#!/bin/bash

set -e

su - melpon -c "
set -e
cd site_generator
git pull
git submodule update -i

export DOCKER_IT=\"\"

./partial-hook/kunai.sh

./docker.sh build
./docker.sh run settings.cpprefjp \"$@\"

cd cpprefjp/cpprefjp.github.io
git add ./ --all
git commit -a \"--author=cpprefjp-autoupdate <shigemasa7watanabe@gmail.com>\" -m \"update automatically\"
git push origin master 2>/dev/null
"
