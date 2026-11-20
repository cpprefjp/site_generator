# -*- coding: utf-8 -*-

"""ページの編集者 (コミットの author) を収集し、GitHub アカウントと紐付ける

メールアドレスから GitHub アカウント名への変換は以下の順で行う。

1. `<id>+<login>@users.noreply.github.com` / `<login>@users.noreply.github.com`
   形式のメールアドレスであれば、そこからアカウント名を取り出す。
2. それ以外は GitHub API (GET /repos/{owner}/{repo}/commits/{sha}) で、
   そのメールアドレスで行われたコミットの `author.login` を取得する。
   メールアドレスを公開していないユーザーでも、GitHub アカウントに
   メールアドレスを登録していれば取得できる。

3. 上記で GitHub アカウントと紐付かなかったメールアドレスは、同じ author 名で
   別のメールアドレスが紐付いていれば、そのアカウントとみなす
   (author 名が複数のアカウントに紐付く場合は曖昧なので行わない)。

結果はキャッシュファイル (JSON) に保存し、次回以降は API を呼ばない。
GitHub アカウントと紐付いていないメールアドレスは null として保存する。
null のエントリを削除すれば、次回の実行時に再度問い合わせる。

環境変数 GITHUB_TOKEN が設定されていれば API の認証に利用する。
未設定の場合は未認証 (60 リクエスト/時) で問い合わせ、レート制限に
達したらそこで打ち切る (残りは次回以降の実行で解決される)。
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request


_NOREPLY_RE = re.compile(r'^(?:\d+\+)?([^@+]+)@users\.noreply\.github\.com$', re.IGNORECASE)


def _warn(message):
    print('contributors: {}'.format(message), file=sys.stderr)


def parse_noreply_email(email):
    m = _NOREPLY_RE.match(email)
    return m.group(1) if m else None


def normalize_name(name):
    """author 名の比較用キー (前後の空白・連続する空白・大文字小文字の違いを無視する)"""
    return ' '.join(name.split()).casefold()


def is_bot_login(login):
    return login is not None and login.endswith('[bot]')


def collect_page_authors(input_dir):
    """input_dir 内の全 .md ファイルについて、編集したコミットの author を収集する

    git log を 1 回だけ実行して全ページ分を集計する。

    戻り値は (page_authors, email_to_sha) のタプル。
    page_authors は {ページのパス (拡張子なし): [author, ...]} で、
    author は {'name', 'email', 'commits', 'last_updated'} の辞書。
    リストは最後に編集した日時が新しい順に並ぶ。
    email_to_sha は {メールアドレス (小文字): そのメールアドレスによる最新コミットのハッシュ}。
    """
    output = subprocess.check_output(
        ['git', 'log', '-z', '--no-renames', '--format=%x1e%H%x09%at%x09%aN%x09%aE', '--name-only', '--', '*.md'],
        cwd=input_dir, text=True, errors='ignore')

    page_authors = {}
    email_to_sha = {}
    for record in output.split('\x1e'):
        if not record:
            continue
        header, _, files = record.partition('\0')
        fields = header.split('\t', 3)
        if len(fields) != 4:
            continue
        sha, timestamp, name, email = fields
        email = email.strip()
        if not email:
            continue
        key = email.lower()
        email_to_sha.setdefault(key, sha)

        for file in files.split('\0'):
            file = file.strip('\n')
            if not file.endswith('.md'):
                continue
            path = file[:-len('.md')]
            # git log は新しいコミットから順に出力するので、
            # 最初に出てきたときの名前・日時がそのページでの最新のものになる
            authors = page_authors.setdefault(path, {})
            if key in authors:
                authors[key]['commits'] += 1
            else:
                authors[key] = {
                    'name': name,
                    'email': email,
                    'commits': 1,
                    'last_updated': int(timestamp),
                }

    # dict は挿入順を保持するので、そのまま最終編集日時の新しい順になっている
    return {path: list(authors.values()) for path, authors in page_authors.items()}, email_to_sha


class GitHubUserResolver(object):
    """メールアドレスから GitHub アカウント名を引く (結果はファイルにキャッシュする)"""

    API_URL_FORMAT = 'https://api.github.com/repos/{repo}/commits/{sha}'

    def __init__(self, cache_file, repo, token=None, timeout=10):
        self._cache_file = cache_file
        self._repo = repo
        self._token = token
        self._timeout = timeout
        try:
            with open(cache_file, encoding='utf-8') as f:
                self._cache = json.load(f)
        except FileNotFoundError:
            self._cache = {}
        except Exception as e:
            _warn('failed to load {}: {}'.format(cache_file, e))
            self._cache = {}
        self._name_to_login = {}

    def _get_by_email(self, email):
        login = parse_noreply_email(email)
        if login is not None:
            return login
        return self._cache.get(email.lower())

    def get(self, email, name=None):
        """メールアドレスから GitHub アカウント名を返す

        メールアドレスで紐付かない場合は、name (author 名) で紐付いている
        アカウント名を返す (build_name_index() を呼んでおく必要がある)。
        """
        login = self._get_by_email(email)
        if login is None and name:
            login = self._name_to_login.get(normalize_name(name))
        return login

    def build_name_index(self, page_authors):
        """author 名から GitHub アカウント名への対応表を作る

        page_authors は collect_page_authors() の戻り値の 1 つ目。
        1 つの author 名が複数のアカウントに紐付く場合 (同姓同名の別人など) は
        曖昧なので対応表に入れない。
        """
        candidates = {}
        for authors in page_authors.values():
            for author in authors:
                login = self._get_by_email(author['email'])
                if login is None:
                    continue
                key = normalize_name(author['name'])
                if key:
                    candidates.setdefault(key, set()).add(login.lower())
                    self._name_to_login.setdefault(key, login)
        for key, logins in candidates.items():
            if len(logins) > 1:
                del self._name_to_login[key]

    def resolve(self, email_to_sha):
        """キャッシュに無いメールアドレスについて GitHub アカウント名を問い合わせる"""
        targets = [(email, sha) for email, sha in email_to_sha.items()
                   if parse_noreply_email(email) is None and email not in self._cache]
        if not targets:
            return

        print('contributors: resolving {} email address(es) via GitHub API'.format(len(targets)))
        resolved = 0
        for email, sha in targets:
            ok, login = self._fetch_commit_author(sha)
            if not ok:
                break
            self._cache[email] = login
            resolved += 1

        if resolved < len(targets):
            _warn('{} email address(es) are left unresolved; they will be retried on the next run'.format(len(targets) - resolved))
        self._flush()

    def _fetch_commit_author(self, sha):
        """コミットの author のアカウント名を取得する

        戻り値は (処理を継続してよいか, アカウント名 or None)。
        """
        url = self.API_URL_FORMAT.format(repo=self._repo, sha=sha)
        headers = {
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'site_generator',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        if self._token:
            headers['Authorization'] = 'Bearer {}'.format(self._token)

        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=self._timeout) as res:
                data = json.load(res)
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                _warn('GitHub API rate limit exceeded (HTTP {}). Set GITHUB_TOKEN to raise the limit.'.format(e.code))
                return False, None
            # 404/422: コミットが GitHub 上に存在しない (push されていない等)。
            # キャッシュはせずに次へ進む。
            _warn('failed to fetch commit {} (HTTP {})'.format(sha, e.code))
            return True, None
        except Exception as e:
            _warn('failed to access GitHub API: {}'.format(e))
            return False, None

        author = data.get('author')
        return True, (author or {}).get('login')

    def _flush(self):
        tmp_file = self._cache_file + '.tmp'
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')
        os.replace(tmp_file, self._cache_file)


def make_page_contributors(authors, resolver):
    """ページの author リストを、テンプレートで表示するための contributor リストに変換する

    同じ GitHub アカウントに紐付く複数のメールアドレスは 1 人にまとめる。
    GitHub アカウントに紐付かない人は、author 名が同じであれば 1 人にまとめる。
    bot アカウントは除外する。
    """
    contributors = []
    by_login = {}
    by_name = {}
    for author in authors:
        login = resolver.get(author['email'], author['name']) if resolver else None
        if is_bot_login(login):
            continue
        if login is not None:
            key = login.lower()
            if key in by_login:
                by_login[key]['commits'] += author['commits']
                continue
            contributor = {
                'name': author['name'],
                'login': login,
                'url': 'https://github.com/{}'.format(login),
                'avatar_url': 'https://github.com/{}.png?size=40'.format(login),
                'commits': author['commits'],
            }
            by_login[key] = contributor
        else:
            key = normalize_name(author['name'])
            if key in by_name:
                by_name[key]['commits'] += author['commits']
                continue
            contributor = {
                'name': author['name'],
                'login': None,
                'url': None,
                'avatar_url': None,
                'commits': author['commits'],
            }
            by_name[key] = contributor
        contributors.append(contributor)
    return contributors
