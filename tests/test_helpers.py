# -*- coding: utf8 -*-
from nose.tools import eq_

from packager.main import _slugify, escape_all


def test_slugify():
    def check(name, slug):
        eq_(_slugify(name), slug)
    check(' Jack & Jill like numbers 1,2,3 and silly characters -_?%.$!/',
          'jack__jill_like_numbers_123_and_silly_characters__')
    check(u"Un \xe9l\xe9phant \xe0 l'or\xe9e du bois",
          u'un_\xe9l\xe9phant_\xe0_lor\xe9e_du_bois')
    check('版本历史记录', 'addon')
    check('版本历史记录booop版', 'booop')
    check('', 'addon')
    check('____', 'addon')
    check('x' * 51, 'x' * 50)


def test_escape_all():
    def check(s, expected):
        eq_(escape_all(s), expected)

    # Test strings.
    check('<a href="http://gkoberger.net/">spam</a>',
          '&lt;a href="http://gkoberger.net/"&gt;spam&lt;/a&gt;')
    check('Just wanted to say <script>alert("hey, brother")</div>',
          'Just wanted to say &lt;script&gt;alert("hey, brother")&lt;/div&gt;')

    # Test lists.
    bad = ['x', '<y>', '<z>']
    good = ['x', '&lt;y&gt;', '&lt;z&gt;']
    check(bad, good)

    # Test dictionaries.
    bad = {'name': 'Firefox<script>',
           'min_ver': '0.4<script>',
           'max_ver': '3.*<script>'}
    good = {'name': 'Firefox&lt;script&gt;',
            'min_ver': '0.4&lt;script&gt;',
            'max_ver': '3.*&lt;script&gt;'}
    check(bad, good)

    # Test a list of dictionaries of strings.
    bad = [
        {'name': 'Firefox<b>',
         'min_ver': '0.4<b>',
         'max_ver': '3.*<marquee>'},
        {'name': 'Thunderbird<b>',
         'min_ver': '0.7<b>',
         'max_ver': '1.*<div>'},
        {'name': 'SeaMonkey<b>',
         'min_ver': '0.4<b>',
         'max_ver': '3.*<font>'}
    ]
    good = [
        {'name': 'Firefox&lt;b&gt;',
         'min_ver': '0.4&lt;b&gt;',
         'max_ver': '3.*&lt;marquee&gt;'},
        {'name': 'Thunderbird&lt;b&gt;',
         'min_ver': '0.7&lt;b&gt;',
         'max_ver': '1.*&lt;div&gt;'},
        {'name': 'SeaMonkey&lt;b&gt;',
         'min_ver': '0.4&lt;b&gt;',
         'max_ver': '3.*&lt;font&gt;'}
    ]
    check(bad, good)
