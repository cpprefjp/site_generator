#!/bin/bash

export DOCKER_IT=""

rm -rf cpprefjp/static/static/kunai || true
mkdir -p cpprefjp/static/static/kunai

if [ ! -d kunai ]; then
  git clone git@github.com:cpprefjp/kunai.git
else
  pushd kunai
  git pull || (cd .. && rm -rf kunai && git clone git@github.com:cpprefjp/kunai.git)
  popd
fi
./kunai/docker.sh build
./kunai/docker.sh install
./kunai/docker.sh run build
cp -r ./kunai/dist/* ./cpprefjp/static/static/kunai/

