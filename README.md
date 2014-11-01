site_generator
==============

`site_generator` は、mdファイルを自動的にhtmlに変換し、github.ioに反映するツールです。

## Requirements

```
pip install -r requirements.txt
```

## ローカルでhtmlに変換する

### cpprefjp の場合

```python
$ git clone https://github.com/cpprefjp/site.git cpprefjp/site
$ ./run.py settings.cpprefjp
```

これで `cpprefjp/cpprefjp.github.io` に html が入ります。

### boostjp の場合

```python
$ git clone https://github.com/boostjp/site.git boostjp/site
$ ./run.py settings.boostjp
```

これで `boostjp/boostjp.github.io` に html が入ります。
