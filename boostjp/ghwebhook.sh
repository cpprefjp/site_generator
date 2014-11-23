#!/bin/bash

set -ex

su - melpon -c "
set -ex
cd site_generator
git pull
source venv/bin/activate

pushd boostjp/site && git pull && popd

./run.py settings.boostjp \"$@\"

cd boostjp/boostjp.github.io
git add ./ --all
git commit -a \"--author=boostjp-autoupdate <shigemasa7watanabe@gmail.com>\" -m \"update automatically\"
git push origin master
"
