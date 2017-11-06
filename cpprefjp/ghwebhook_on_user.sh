#!/bin/bash

set -e
git pull
git submodule update -i

rm -rf cpprefjp/static/static/kunai || true
mkdir -p cpprefjp/static/static/kunai
rm -rf cpprefjp/static/static/crsearch || true
mkdir -p cpprefjp/static/static/crsearch

export DOCKER_IT=""

function rm_rf() {
  docker run -v `pwd`:/var/src alpine:3.6 /bin/sh -c "rm -rf /var/src/$1 || true"
}
function clone_and_fallback() {
  if [ ! -d $1/.git ]; then
    rm_rf $1
    git clone $2 $1
  else
    pushd $1
    if git pull; then
      popd
    else
      popd
      rm_rf $1
      git clone $2 $1
    fi
  fi
}
function clone_and_initsubmodule_and_fallback() {
  clone_and_fallback "$@"
  pushd $1
  if git submodule update -i; then
    popd
  else
    popd
    rm_rf $1
    git clone $2 $1
    pushd $1
    git submodule update -i
    popd
  fi
}

# kunai 用 JS, CSS 生成
clone_and_initsubmodule_and_fallback kunai git@github.com:cpprefjp/kunai.git
./kunai/docker.sh build
./kunai/docker.sh install
cp -r ./kunai/dist/* ./cpprefjp/static/static/kunai/

# crsearch.json 生成
clone_and_fallback crsearch.json/site git@github.com:cpprefjp/site.git
./crsearch.json/docker.sh build
./crsearch.json/docker.sh run
cp crsearch.json/crsearch.json cpprefjp/static/static/crsearch/

# サイト生成
clone_and_fallback cpprefjp/cpprefjp.github.io git@github.com:cpprefjp/cpprefjp.github.io.git
clone_and_fallback cpprefjp/site git@github.com:cpprefjp/site.git
./docker.sh build
./docker.sh run settings.cpprefjp "$@"

cd cpprefjp/cpprefjp.github.io
git add ./ --all
git commit -a "--author=cpprefjp-autoupdate <shigemasa7watanabe@gmail.com>" -m "update automatically"
git push origin master 2>/dev/null
