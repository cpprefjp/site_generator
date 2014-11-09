#!/bin/bash

set -ex

su - melpon -c '
set -ex
cd site_generator
source venv/bin/activate

pushd boostjp/site && git pull && popd

rm -r boostjp/boostjp.github.io/*
./run.py settings.boostjp

cd boostjp/boostjp.github.io
git add ./ --all
git commit -a "--author=boostjp-autoupdate <shigemasa7watanabe@gmail.com>"
git push origin master
'
