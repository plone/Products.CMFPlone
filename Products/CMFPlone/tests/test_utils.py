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
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.tests.base.content import FAUX_HTML_LEADING_TEXT
from Products.CMFCore.tests.base.content import SIMPLE_HTML
from Products.CMFCore.tests.base.content import SIMPLE_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import SIMPLE_XHTML
from Products.CMFCore.tests.base.content import STX_WITH_HTML

from Products.CMFPlone.interfaces import ISiteSchema
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


SITE_LOGO_BASE64 = 'filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgAA'\
                   'AAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAAAA'\
                   'ElFTkSuQmCC'


class DefaultUtilsTests(unittest.TestCase):

    def test_bodyfinder(self):
        from Products.CMFPlone.utils import bodyfinder

        self.assertEqual(bodyfinder(FAUX_HTML_LEADING_TEXT),
                         '\n  <h1>Not a lot here</h1>\n ')
        self.assertEqual(bodyfinder(SIMPLE_HTML),
                         '\n  <h1>Not a lot here</h1>\n ')
        self.assertEqual(bodyfinder(SIMPLE_STRUCTUREDTEXT),
                         SIMPLE_STRUCTUREDTEXT)
        self.assertEqual(bodyfinder(SIMPLE_XHTML),
                         '\n  <h1>Not a lot here</h1>\n ')
        self.assertEqual(bodyfinder(STX_WITH_HTML),
                         '<p>Hello world, I am Bruce.</p>')


class LogoTests(PloneTestCase.PloneTestCase):
    def test_getSiteLogo_with_setting(self):
        from Products.CMFPlone.utils import getSiteLogo
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        settings.site_logo = SITE_LOGO_BASE64

        self.assertTrue(
            'http://nohost/plone/@@site-logo/pixel.png'
            in getSiteLogo())

    def test_getSiteLogo_with_no_setting(self):
        from Products.CMFPlone.utils import getSiteLogo
        self.assertTrue(
            'http://nohost/plone/logo.png'
            in getSiteLogo())
