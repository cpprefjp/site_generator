#!/bin/bash

set -e

su - melpon -c "
set -e
cd site_generator
git pull
git submodule update -i


rm -rf cpprefjp/static/static/crsearch || true
mkdir -p cpprefjp/static/static/crsearch

export DOCKER_IT=\"\"

./partial-hook/kunai.sh


# crsearch.json 生成
if [ ! -d crsearch.json/site ]; then
  git clone git@github.com:cpprefjp/site.git crsearch.json/site
else
  pushd crsearch.json/site
  git pull || (cd .. && rm -rf site && git clone git@github.com:cpprefjp/site.git)
  popd
fi
./crsearch.json/docker.sh build
./crsearch.json/docker.sh run
cp crsearch.json/crsearch.json cpprefjp/static/static/crsearch/

# サイト生成
if [ ! -d cpprefjp/site ]; then
  git clone git@github.com:cpprefjp/site.git cpprefjp/site
else
  pushd cpprefjp/site
  git pull || (cd .. && rm -rf site && git clone git@github.com:cpprefjp/site.git)
  popd
fi

./docker.sh build
./docker.sh run settings.cpprefjp \"$@\"

cd cpprefjp/cpprefjp.github.io
git add ./ --all
git commit -a \"--author=cpprefjp-autoupdate <shigemasa7watanabe@gmail.com>\" -m \"update automatically\"
git push origin master 2>/dev/null
"
