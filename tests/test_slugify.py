# -*- coding: utf8 -*-
from nose.tools import eq_

from packager.main import _slugify


def test_slugify():
    def check(name, slug):
        eq_(_slugify(name), slug)
    check(' Jack & Jill like number 1,2,3 and 4 and silly characters -_?%.$!/',
          'jack__jill_like_number_123_and_4_and_silly_characters___')
    check(u"Un \xe9l\xe9phant \xe0 l'or\xe9e du bois",
          u'un_\xe9l\xe9phant_\xe0_lor\xe9e_du_bois')
    check('版本历史记录', 'addon')
    check('版本历史记录boop版', 'boop')
    check('', 'addon')
