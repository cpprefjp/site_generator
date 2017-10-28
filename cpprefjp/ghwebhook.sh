#!/bin/bash

set -e

su - melpon -c "
set -e
cd site_generator
git pull
git submodule update -i
source venv/bin/activate

pushd cpprefjp/site && git pull && popd

./docker.sh build
./docker.sh run settings.cpprefjp \"$@\"

cd cpprefjp/cpprefjp.github.io
git add ./ --all
git commit -a \"--author=cpprefjp-autoupdate <shigemasa7watanabe@gmail.com>\" -m \"update automatically\"
git push origin master 2>/dev/null
"
