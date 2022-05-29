# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# 入力ディレクトリ
INPUT_DIR = 'cpprefjp/site'

# 静的ファイルディレクトリ
STATIC_DIR = 'cpprefjp/static'

# 出力ディレクトリ
OUTPUT_DIR = 'cpprefjp/cpprefjp.github.io'

# URL ベース
BASE_URL = 'https://cpprefjp.github.io'
EDIT_URL_FORMAT = 'https://github.com/cpprefjp/site/edit/master/{path}'
HISTORY_URL_FORMAT = 'https://github.com/cpprefjp/site/commits/master/{path}'
PROJECT_URL = 'https://github.com/cpprefjp/site'
PROJECT_NAME = 'GitHub Project'

# ブランド名
BRAND = 'cpprefjp - C++日本語リファレンス'

# タイトルの後ろに付ける文字列
TITLE_SUFFIX = ' - cpprefjp C++日本語リファレンス'

# テンプレートディレクトリ
PAGE_TEMPLATE_DIR = 'cpprefjp/templates'

# サイドバーの出力を無しにするか
DISABLE_SIDEBAR = True

# HTML の minify を行なうか
USE_MINIFY = False

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
<div class="gcse-search"></div>
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

# sitemap ファイル
SITEMAP_PATH = 'sitemap.xml'

# キーワード
META_KEYWORDS = 'C++,標準ライブラリ,リファレンス,ドキュメント,STL,std'

# cachebust の生成方法
# 'none' => 生成しない
# 'time' => 時間ベース
# 'git' => CACHEBUST_DIR のディレクトリの git rev-parse HEAD の結果を使う
CACHEBUST_TYPE = 'git'
CACHEBUST_DIR = 'kunai'

USE_RELATIVE_LINK = False

# 並び替えルール
ORDER_PRIORITY_LIST = [
    'op_constructor',
    'op_destructor',
    'op_deduction_guide', # 推論補助
    'op_assign',  # operatr=
    'op_at',  # operator[]
    'op_call',  # operator()
    'op_deref',  # operator*
    'op_arrow',  # opeartor->
    '__functions__',  # 通常の関数や非メンバ関数(op_でもtype-でもないもの)
    'op_plus_assign',  # opeartor+=
    'op_minus_assign',  # opeartor-=
    'op_multiply_assign',  # operator*=
    'op_divide_assign',  # operator/=
    'op_modulo_assign',  # opeartor%=
    'op_left_shift_assign',  # operator<<=
    'op_right_shift_assign',  # opeartor>>=
    'op_and_assign',  # operator&=
    'op_or_assign',  # operator|=
    'op_xor_assign',  # operator^=
    'op_increment',  # operator++
    'op_decrement',  # operator--
    'op_unary_plus',  # operator+
    'op_unary_minus',  # operator-
    'op_not',  # operator!
    'op_flip',  # operator~
    '__converter__',  # 変換演算子(ここに列挙した以外で頭にop_が付いているもの)
    'op_equal',  # operator==(a, b)
    'op_not_equal',  # operator!=(a, b)
    'op_less',  # operator<(a, b)
    'op_less_equal',  # operator<=(a, b)
    'op_greater',  # operator>(a, b)
    'op_greater_equal',  # operator>=(a, b)
    'op_compare_3way', # operator<=>(a, b)
    'op_plus',  # operator+(a, b)
    'op_minus',  # operator-(a, b)
    'op_multiply',  # operator*(a, b)
    'op_divide',  # operator/(a, b)
    'op_modulo',  # operator%(a, b)
    'op_and',  # operator&(a, b)
    'op_or',  # operator|(a, b)
    'op_xor',  # operator^(a, b)
    'op_logical_and',  # operator&&(a, b)
    'op_logical_or',  # operator||(a, b)
    'op_left_shift',  # operator<<(a, b)
    'op_right_shift',  # opeartor>>(a, b)
    'op_ostream',  # operator<<(os, b)
    'op_istream',  # operator>>(is, b)
    '__types__',  # メンバ型（頭にtype-が付いているもの）
]
ORDER_PRIORITY = {v: n for n, v in enumerate(ORDER_PRIORITY_LIST)}


def get_order_priority(name):
    if name.startswith('op_'):
        if name in ORDER_PRIORITY:
            return ORDER_PRIORITY[name]
        return ORDER_PRIORITY['__converter__']
    elif name.startswith('type-'):
        return ORDER_PRIORITY['__types__']
    else:
        return ORDER_PRIORITY['__functions__']
