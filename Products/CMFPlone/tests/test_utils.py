""" Unit tests for utils module. """

from plone.registry.interfaces import IRegistry
from Products.CMFCore.tests.base.content import FAUX_HTML_LEADING_TEXT
from Products.CMFCore.tests.base.content import SIMPLE_HTML
from Products.CMFCore.tests.base.content import SIMPLE_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import SIMPLE_XHTML
from Products.CMFCore.tests.base.content import STX_WITH_HTML
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getUtility
from zope.interface import alsoProvides
from plone.subrequest.interfaces import ISubRequest

import unittest


SITE_LOGO_BASE64 = b'filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgA'\
                   b'AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA'\
                   b'AAElFTkSuQmCC'


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

    def test_safe_encode(self):
        """safe_encode should always encode unicode to the specified encoding.
        """
        from Products.CMFPlone.utils import safe_encode
        self.assertEqual(safe_encode('späm'), b'sp\xc3\xa4m')
        self.assertEqual(safe_encode('späm', 'utf-8'), b'sp\xc3\xa4m')
        self.assertEqual(safe_encode('späm', encoding='latin-1'), b'sp\xe4m')

    def test_get_top_request(self):
        """If in a subrequest, ``get_top_request`` should always return the top
        most request.
        """
        from Products.CMFPlone.utils import get_top_request

        class MockRequest:

            def __init__(self, parent_request=None):
                self._dict = {}
                if parent_request:
                    self._dict['PARENT_REQUEST'] = parent_request
                    alsoProvides(self, ISubRequest)

            def get(self, key, default=None):
                return self._dict.get(key, default)

        req0 = MockRequest()
        req1 = MockRequest(req0)
        req2 = MockRequest(req1)

        self.assertEqual(get_top_request(req0), req0)
        self.assertEqual(get_top_request(req1), req0)
        self.assertEqual(get_top_request(req2), req0)

    def test_get_top_site_from_url(self):
        """Unit test for ``get_top_site_from_url`` with context and request
        mocks.

        Test content structure:
        /approot/PloneSite/folder/SubSite/folder
        PloneSite and SubSite implement ISite
        """
        from plone.app.content.browser.contents import get_top_site_from_url
        from urllib.parse import urlparse
        from zope.component.interfaces import ISite

        class MockContext:
            vh_url = 'http://nohost'
            vh_root = ''

            def __init__(self, physical_path):
                self.physical_path = physical_path
                if self.physical_path.split('/')[-1] in ('PloneSite', 'SubSite'):  # noqa
                    alsoProvides(self, ISite)

            @property
            def id(self):
                return self.physical_path.split('/')[-1]

            def absolute_url(self):
                return self.vh_url + self.physical_path[len(self.vh_root):] or '/'  # noqa

            def restrictedTraverse(self, path):
                return MockContext(self.vh_root + path)

        class MockRequest:
            vh_url = 'http://nohost'
            vh_root = ''

            def physicalPathFromURL(self, url):
                # Return the physical path from a URL.
                # The outer right '/' is not part of the path.
                path = self.vh_root + urlparse(url).path.rstrip('/')
                return path.split('/')

        # NO VIRTUAL HOSTING

        req = MockRequest()

        # Case 1:
        ctx = MockContext('/approot/PloneSite')
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'PloneSite')

        # Case 2
        ctx = MockContext('/approot/PloneSite/folder')
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'PloneSite')

        # Case 3:
        ctx = MockContext('/approot/PloneSite/folder/SubSite/folder')
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'PloneSite')

        # Case 4, using unicode paths accidentially:
        ctx = MockContext('/approot/PloneSite/folder/SubSite/folder')
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'PloneSite')

        # VIRTUAL HOSTING ON SUBSITE

        req = MockRequest()
        req.vh_root = '/approot/PloneSite/folder/SubSite'

        # Case 4:
        ctx = MockContext('/approot/PloneSite/folder/SubSite')
        ctx.vh_root = '/approot/PloneSite/folder/SubSite'
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'SubSite')

        # Case 5:
        ctx = MockContext('/approot/PloneSite/folder/SubSite/folder')
        ctx.vh_root = '/approot/PloneSite/folder/SubSite'
        self.assertEqual(get_top_site_from_url(ctx, req).id, 'SubSite')

    def test_human_readable_size_int(self):
        from Products.CMFPlone.utils import human_readable_size

        self.assertEqual(human_readable_size(0), '0 KB')
        self.assertEqual(human_readable_size(1), '1 KB')
        size = 1000
        self.assertEqual(human_readable_size(size), '1 KB')
        size += 24
        self.assertEqual(human_readable_size(size), '1.0 KB')
        size += 512
        self.assertEqual(human_readable_size(size), '1.5 KB')
        size *= 1024
        self.assertEqual(human_readable_size(size), '1.5 MB')
        size *= 1024
        self.assertEqual(human_readable_size(size), '1.5 GB')
        size *= 1024
        self.assertEqual(human_readable_size(size), '1536.0 GB')

    def test_human_readable_size_float(self):
        from Products.CMFPlone.utils import human_readable_size

        self.assertEqual(human_readable_size(0.), '0 KB')
        self.assertEqual(human_readable_size(1.), '1 KB')
        size = 1000.
        self.assertEqual(human_readable_size(size), '1 KB')
        size += 24.
        self.assertEqual(human_readable_size(size), '1.0 KB')
        size += 512.
        self.assertEqual(human_readable_size(size), '1.5 KB')
        size *= 1024.
        self.assertEqual(human_readable_size(size), '1.5 MB')
        size *= 1024.
        self.assertEqual(human_readable_size(size), '1.5 GB')
        size *= 1024.
        self.assertEqual(human_readable_size(size), '1536.0 GB')

    def test_human_readable_size_special(self):
        from Products.CMFPlone.utils import human_readable_size

        self.assertEqual(human_readable_size(None), '0 KB')
        self.assertEqual(human_readable_size(''), '0 KB')
        self.assertEqual(human_readable_size('barney'), 'barney')


class LogoTests(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

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
