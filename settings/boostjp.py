# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# 入力ディレクトリ
INPUT_DIR = 'boostjp/site'

# 静的ファイルディレクトリ
STATIC_DIR = 'boostjp/static'

# 出力ディレクトリ
OUTPUT_DIR = 'boostjp/boostjp.github.io'

# URL ベース
BASE_URL = 'https://boostjp.github.io'
EDIT_URL_FORMAT = 'https://github.com/boostjp/site/edit/master/{path}'
HISTORY_URL_FORMAT = 'https://github.com/boostjp/site/commits/master/{path}'
PROJECT_URL = 'https://github.com/boostjp/site'
PROJECT_NAME = 'GitHub Project'

# ブランド名
BRAND = 'boostjp : Boost日本語情報サイト'

# タイトルの後ろに付ける文字列
TITLE_SUFFIX = ' - boostjp'

# テンプレートディレクトリ
PAGE_TEMPLATE_DIR = 'boostjp/templates'

# サイドバーの出力を無しにするか
DISABLE_SIDEBAR = False

# HTML の minify を行なうか
USE_MINIFY = True

# 検索用 HTML
GOOGLE_SITE_SEARCH = '''
<script>
  (function() {
    var cx = '013316413321391058734:dma_peph4n0';
    var gcse = document.createElement('script');
    gcse.type = 'text/javascript';
    gcse.async = true;
    gcse.src = (document.location.protocol == 'https:' ? 'https:' : 'http:') +
        '//www.google.com/cse/cse.js?cx=' + cx;
    var s = document.getElementsByTagName('script')[0];
    s.parentNode.insertBefore(gcse, s);
  })();
</script>
<gcse:searchbox></gcse:searchbox>
'''

# Google Analytics
GOOGLE_ANALYTICS = '''
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-56896607-2', 'auto');
  ga('send', 'pageview');

</script>
'''

# RSS ファイル
RSS_PATH = 'rss.xml'

# sitemap ファイル
SITEMAP_PATH = 'sitemap.xml'

# キーワード
META_KEYWORDS = 'C++,Boost,リファレンス,ドキュメント'


# 並び替えルール
def get_order_priority(name):
    return 1
