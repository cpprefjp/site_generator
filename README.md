site_generator
==============

`site_generator` は、mdファイルを自動的にhtmlに変換し、github.ioに反映するツールです。

## ソースコードの取得

```bash
$ git clone https://github.com/cpprefjp/site_generator.git
$ cd site_generator
$ git submodule update --init
```

## ローカルで動作を確認する

まず Docker をインストールする必要があります。

- Macの場合: [Docker for Mac](https://www.docker.com/docker-mac) をインストール
- Ubuntuの場合: [公式ドキュメント](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/) に書いてある通りにコマンドを実行してインストール

### cpprefjp の場合

準備:

```bash
git clone https://github.com/cpprefjp/site.git cpprefjp/site
git clone https://github.com/cpprefjp/image.git cpprefjp/image

# kunai 用のデータを生成する
git clone https://github.com/cpprefjp/kunai.git
cd kunai
git submodule update --init
cd ..
./kunai/docker.sh build
./kunai/docker.sh install
./kunai/docker.sh dist
# 生成した kunai の静的ファイルに対するシンボリックリンクを作る
pushd cpprefjp/static/static
ln -s ../../../kunai/dist kunai
popd

# crsearch 用のデータを生成する
./crsearch.json/docker.sh build
./crsearch.json/docker.sh run
# 生成した crsearch の静的ファイルに対するシンボリックリンクを作る
mkdir -p cpprefjp/static/static/crsearch
pushd cpprefjp/static/static/crsearch
ln -s ../../../../crsearch.json/crsearch.json crsearch.json
ln -s ../../../../crsearch.json/crsearch.js crsearch.js # Optional (ローカル file:///... で閲覧する場合に必要)
popd

# site_generator 用の docker イメージを生成する
./docker.sh build
```

実行:

```bash
# この辺は必要に応じて実行する
(cd cpprefjp/site && git pull)
(cd cpprefjp/image && git pull)
./crsearch.json/docker.sh run
./kunai/docker.sh run build

./docker.sh run settings.cpprefjp_local
./docker.sh localhost cpprefjp
```

これでローカルサーバが起動します。
http://localhost:8000 を開けば `index.html` が表示されます。

`run.py`のコマンドライン引数として`--prefix=lang/cpp17/`のように指定すれば、`lang/cpp17/`ディレクトリ階層以下のみが変換されます。

### boostjp の場合

準備:

```bash
git clone https://github.com/boostjp/site.git boostjp/site
git clone https://github.com/boostjp/image.git boostjp/image

# site_generator 用の docker イメージを生成する
./docker.sh build
```

実行:

```bash
./docker.sh run settings.boostjp_local
./docker.sh localhost boostjp
```

これでローカルサーバが起動します。
http://localhost:8000 を開けば `index.html` が表示されます。

## 編集者の GitHub アイコン表示

settings に `GITHUB_REPO` (例: `'cpprefjp/site'`) が設定されている場合、各ページの右上にそのページを編集した人の GitHub アイコンを表示します。

- コミットのメールアドレスから GitHub アカウント名への変換結果は `<setting>.github_users.cache` (例: `settings.cpprefjp.github_users.cache`) に JSON 形式でキャッシュされます。
- 変換には GitHub API を使います。環境変数 `GITHUB_TOKEN` を設定しておくと、認証付きで問い合わせるためレート制限 (未認証だと 60 リクエスト/時) にかかりにくくなります。`./docker.sh run` は `GITHUB_TOKEN` をコンテナに引き継ぎます。トークンには公開リポジトリの読み取り権限があれば十分です。
- レート制限などで変換できなかったメールアドレスは、次回実行時に再度問い合わせます。GitHub アカウントと紐付いていないメールアドレスはキャッシュに `null` として保存され、そのエントリを削除すると再度問い合わせます。

## コーディング規約（開発者向け）

ルールは１つです。
`./docker.sh coding` を実行してエラーが出ないようにして下さい。
これはPEP8、Flake8、Hackingあたりの規約を少し緩めて混ぜた規約になっています。
