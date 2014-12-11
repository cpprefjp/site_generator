#coding: utf-8

# 入力ディレクトリ
INPUT_DIR = 'cpprefjp/site'

# 静的ファイルディレクトリ
STATIC_DIR = 'cpprefjp/static'

# 出力ディレクトリ
OUTPUT_DIR = 'cpprefjp/cpprefjp.github.io'

# URL ベース
BASE_URL = 'http://cpprefjp.github.io'
EDIT_URL_FORMAT = 'https://github.com/cpprefjp/site/edit/master/{path}'
PROJECT_URL = 'https://github.com/cpprefjp/site'
PROJECT_NAME = 'GitHub Project'

# ブランド名
BRAND = 'cpprefjp - C++ Reference Site'

# タイトルの後ろに付ける文字列
TITLE_SUFFIX = ' - cpprefjp'

# テンプレートディレクトリ
PAGE_TEMPLATE_DIR = 'cpprefjp/templates'

# HTML の minify を行なうか
USE_MINIFY = True

# 検索用 HTML
GOOGLE_SITE_SEARCH = '''
<script>
  (function() {
    var cx = '013316413321391058734:ji_u66hl7hq';
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

  ga('create', 'UA-56896607-1', 'auto');
  ga('send', 'pageview');
</script>
'''

# RSS ファイル
RSS_PATH = 'rss.xml'
