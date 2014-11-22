#!/bin/bash

set -ex

su - melpon -c '
set -ex
cd site_generator
git pull
source venv/bin/activate

pushd cpprefjp/site && git pull && popd

./run.py settings.cpprefjp

cd cpprefjp/cpprefjp.github.io
git add ./ --all
git commit -a "--author=cpprefjp-autoupdate <shigemasa7watanabe@gmail.com>" -m "update automatically"
git push origin master
'
