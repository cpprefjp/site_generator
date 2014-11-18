#coding: utf-8

# 入力ディレクトリ
INPUT_DIR = 'cpprefjp/site'

# 出力ディレクトリ
OUTPUT_DIR = 'cpprefjp/cpprefjp.github.io'

# URL ベース
BASE_URL = 'http://cpprefjp.github.io'
EDIT_URL_FORMAT = 'https://github.com/cpprefjp/site/edit/master/{paths}'

# ブランド名
BRAND = 'cpprefjp - C++ Library Reference'

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
