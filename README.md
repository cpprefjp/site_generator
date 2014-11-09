site_generator
==============

`site_generator` は、mdファイルを自動的にhtmlに変換し、github.ioに反映するツールです。

## ソースコードの取得

```
$ git clone https://github.com/cpprefjp/site_generator.git
$ git submodule update -i
```

## ローカルで動作を確認する

### Requirements

Python を使っているので、依存するライブラリを以下のようにインストールします。

```
$ pip install -r requirements.txt
```

### cpprefjp の場合

```python
$ git clone https://github.com/cpprefjp/site.git cpprefjp/site
$ ./run.py settings.cpprefjp_local
$ ./localhost.sh cpprefjp/cpprefjp.github.io
```

これでローカルサーバが起動します。
http://localhost:8000 を開けば `index.html` が表示されます。

### boostjp の場合

```python
$ git clone https://github.com/boostjp/site.git boostjp/site
$ ./run.py settings.boostjp_local
$ ./localhost.sh boostjp/boostjp.github.io
```

これでローカルサーバが起動します。
http://localhost:8000 を開けば `index.html` が表示されます。

