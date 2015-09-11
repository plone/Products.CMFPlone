import unittest

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummyContent

from Acquisition import aq_parent
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ILoginSchema
from zope.component import getSiteManager


class DummyFolder(DummyFolder):
    def absolute_url(self):
        return '/'.join([aq_parent(self).absolute_url(), self.getId()])


class DummyLoginSettings():
    allow_external_login_sites = [
        'http://external1',
        'http://external2/',
        'http://external3/site',
        'http://external4/site/'
        ]

class DummyRegistry(DummyContent):


    def __getitem__(self, name, default=None):
        if name == 'plone.allow_external_login_sites':
            return DummyLoginSettings().allow_external_login_sites
        return default

    def forInterface(self, iface, prefix=''):
    	if iface == ILoginSchema:
    		return DummyLoginSettings()



class TestURLTool(unittest.TestCase):

    def setUp(self):
        self.site = DummySite(id='foo')
        self.site._setObject('foo', DummyFolder(id='foo'))
        self.site.foo._setObject('doc1', DummyContent(id='doc1'))
        mock_registry = DummyRegistry(id='portal_registry')
        self.site.portal_registry = mock_registry
        sm = getSiteManager()
        sm.registerUtility(component=mock_registry, provided=IRegistry)

    def _makeOne(self, *args, **kw):
        from Products.CMFPlone.URLTool import URLTool
        url_tool = URLTool(*args, **kw)
        return url_tool.__of__(self.site)

    def test_isURLInPortal(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal
        self.assertTrue(iURLiP('http://www.foobar.com/bar/foo/folder'))
        self.assertTrue(iURLiP('http://www.foobar.com/bar/foo'))
        self.assertFalse(iURLiP('http://www.foobar.com/bar2/foo'))
        self.assertTrue(iURLiP('https://www.foobar.com/bar/foo/folder'))
        self.assertFalse(iURLiP('http://www.foobar.com:8080/bar/foo/folder'))
        self.assertFalse(iURLiP('http://www.foobar.com/bar'))
        self.assertFalse(iURLiP('/images'))
        self.assertTrue(iURLiP('/bar/foo/foo'))

    def test_isURLInPortalRelative(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal

        #non-root relative urls will need a current context to be passed in
        self.assertTrue(iURLiP('images/img1.jpg'))
        self.assertTrue(iURLiP('./images/img1.jpg'))

        # /bar/foo/something
        self.assertTrue(iURLiP('../something', self.site.foo.doc1))
        # /bar/afolder
        self.assertFalse(iURLiP('../../afolder', self.site.foo.doc1))
        # /afolder
        self.assertFalse(iURLiP('../../../afolder', self.site.foo.doc1))

        # /../afolder? How do we have more ../'s than there are parts in
        # the URL?
        self.assertFalse(iURLiP('../../../../afolder', self.site.foo.doc1))

        # /bar/foo/afolder
        self.assertTrue(iURLiP('../../foo/afolder', self.site.foo.doc1))

    def test_isURLInPortalExternal(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal
        self.assertTrue(iURLiP('http://external1'))
        self.assertTrue(iURLiP('http://external1/'))
        self.assertTrue(iURLiP('http://external1/something'))
        self.assertTrue(iURLiP('http://external2'))
        self.assertTrue(iURLiP('http://external2/'))
        self.assertTrue(iURLiP('http://external2/something'))
        self.assertTrue(iURLiP('http://external3/site'))
        self.assertTrue(iURLiP('http://external3/site/'))
        self.assertTrue(iURLiP('http://external3/site/something'))
        self.assertTrue(iURLiP('http://external4/site'))
        self.assertTrue(iURLiP('http://external4/site/'))
        self.assertTrue(iURLiP('http://external4/site/something'))

        self.assertFalse(iURLiP('http://external3/other'))
        self.assertFalse(iURLiP('http://external4/other'))
        self.assertFalse(iURLiP('http://external5'))
        self.assertFalse(iURLiP('http://external11'))

    def test_script_tag_url_not_in_portal(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal
        self.assertFalse(iURLiP('<script>alert("hi");</script>'))
        self.assertFalse(
            iURLiP('%3Cscript%3Ealert(%22hi%22)%3B%3C%2Fscript%3E'))

    def test_inline_url_not_in_portal(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal
        self.assertFalse(iURLiP('javascript%3Aalert(3)'))
        self.assertFalse(iURLiP('javascript:alert(3)'))
