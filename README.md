site_generator
==============

`site_generator` は、mdファイルを自動的にhtmlに変換し、github.ioに反映するツールです。

## ソースコードの取得

```
$ git clone https://github.com/cpprefjp/site_generator.git
$ cd site_generator
$ git submodule update -i
```

## ローカルで動作を確認する

### Requirements

Python を使っているので、依存するライブラリを以下のようにインストールします。

```
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

`virtualenv` を使って、以下のようにすることをオススメします。

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

### cpprefjp の場合

```
$ git clone https://github.com/cpprefjp/site.git cpprefjp/site
$ ./run.py settings.cpprefjp_local
$ ./localhost.sh cpprefjp/cpprefjp.github.io
```

これでローカルサーバが起動します。
http://localhost:8000 を開けば `index.html` が表示されます。

`run.py`のコマンドライン引数として`--prefix=lang/cpp17/`のように指定すれば、`lang/cpp17/`ディレクトリ階層以下のみが変換されます。

### boostjp の場合

```
$ git clone https://github.com/boostjp/site.git boostjp/site
$ ./run.py settings.boostjp_local
$ ./localhost.sh boostjp/boostjp.github.io
```

これでローカルサーバが起動します。
http://localhost:8000 を開けば `index.html` が表示されます。

## コーディング規約（開発者向け）

ルールは１つです。
`./coding.sh` を実行してエラーが出ないようにして下さい。
これはPEP8、Flake8、Hackingあたりの規約を少し緩めて混ぜた規約になっています。
