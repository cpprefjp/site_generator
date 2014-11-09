#!/bin/bash

set -ex

su - melpon -c '
set -ex
cd site_generator
source venv/bin/activate

pushd boostjp/site && git pull && popd

rm -r cpprefjp/cpprefjp.github.io/*
./run.py settings.cpprefjp

cd cpprefjp/cpprefjp.github.io
git add ./ --all
git commit -a "--author=cpprefjp-autoupdate <shigemasa7watanabe@gmail.com>" -m "update automatically"
git push origin master
'
