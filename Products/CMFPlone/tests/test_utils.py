##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for utils module. """

import unittest

from Products.CMFCore.tests.base.content import FAUX_HTML_LEADING_TEXT
from Products.CMFCore.tests.base.content import SIMPLE_HTML
from Products.CMFCore.tests.base.content import SIMPLE_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import SIMPLE_XHTML
from Products.CMFCore.tests.base.content import STX_WITH_HTML


class DefaultUtilsTests(unittest.TestCase):

    def test_bodyfinder(self):
        from Products.CMFPlone.utils import bodyfinder

        self.assertEqual( bodyfinder(FAUX_HTML_LEADING_TEXT),
                          '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( bodyfinder(SIMPLE_HTML),
                          '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( bodyfinder(SIMPLE_STRUCTUREDTEXT),
                          SIMPLE_STRUCTUREDTEXT )
        self.assertEqual( bodyfinder(SIMPLE_XHTML),
                          '\n  <h1>Not a lot here</h1>\n ' )
        self.assertEqual( bodyfinder(STX_WITH_HTML),
                          '<p>Hello world, I am Bruce.</p>' )
