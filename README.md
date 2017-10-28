site_generator
==============

`site_generator` は、mdファイルを自動的にhtmlに変換し、github.ioに反映するツールです。

## ソースコードの取得

```bash
$ git clone https://github.com/cpprefjp/site_generator.git
$ cd site_generator
$ git submodule update -i
```

## ローカルで動作を確認する

まず Docker をインストールする必要があります。

- Macの場合: [Docker for Mac](https://www.docker.com/docker-mac) をインストール
- Ubuntuの場合: [公式ドキュメント](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/) に書いてある通りにコマンドを実行してインストール

### cpprefjp の場合

準備:

```bash
git clone https://github.com/cpprefjp/site.git cpprefjp/site

# crsearch を有効にするためにいろいろ準備する
./crsearch.json/docker.sh build
./crsearch.json/docker.sh run
git clone https://github.com/cpprefjp/crsearch.git
./crsearch/docker.sh build
./crsearch/docker.sh install
./crsearch/docker.sh run build

# 生成した静的ファイルに対するシンボリックリンクを作る
cd cpprefjp/static/static
mkdir crsearch || true
cd crsearch
ln -s ../../../../crsearch.json/crsearch.json crsearch.json
for file in `ls -1 ../../../../crsearch/dist`; do
  ln -s ../../../../crsearch/dist/$file $file
done
```

実行:

```bash
# この辺は必要に応じて実行する
./crsearch.json/docker.sh run
./crsearch/docker.sh run

./docker.sh run settings.cpprefjp_local
./docker.sh localhost cpprefjp
```

これでローカルサーバが起動します。
http://localhost:8001 を開けば `index.html` が表示されます。

`run.py`のコマンドライン引数として`--prefix=lang/cpp17/`のように指定すれば、`lang/cpp17/`ディレクトリ階層以下のみが変換されます。

### boostjp の場合

準備:

```bash
git clone https://github.com/boostjp/site.git boostjp/site
```

実行:

```bash
./docker.sh run settings.boostjp_local
./docker.sh localhost boostjp
```

これでローカルサーバが起動します。
http://localhost:8001 を開けば `index.html` が表示されます。

## コーディング規約（開発者向け）

ルールは１つです。
`./docker.sh coding` を実行してエラーが出ないようにして下さい。
これはPEP8、Flake8、Hackingあたりの規約を少し緩めて混ぜた規約になっています。
