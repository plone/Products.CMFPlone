import unittest

from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyFolder
from Products.CMFCore.tests.base.dummy import DummyContent

from Acquisition import aq_parent


class DummyFolder(DummyFolder):
    
    def absolute_url(self):
        return '/'.join([aq_parent(self).absolute_url(), self.getId()])


class DummyProperties(DummyContent):

    _allow_external_login_sites = [
        'http://external1',
        'http://external2/',
        'http://external3/site',
        'http://external4/site/'
        ]

    def getProperty(self, name, default=None):
        if name == 'allow_external_login_sites':
            return self._allow_external_login_sites
        return default


class TestURLTool(unittest.TestCase):

    def setUp(self):
        self.site = DummySite(id='foo')
        self.site._setObject('foo', DummyFolder(id='foo'))
        self.site.foo._setObject('doc1', DummyContent(id='doc1'))
        self.site.portal_properties = DummyProperties(id='portal_properties')
        self.site.portal_properties.site_properties = DummyProperties(id='site_properties')

    def _makeOne(self, *args, **kw):
        from Products.CMFPlone.URLTool import URLTool
        url_tool = URLTool(*args, **kw)
        return url_tool.__of__(self.site)

    def test_isURLInPortal(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal
        self.failUnless(iURLiP('http://www.foobar.com/bar/foo/folder'))
        self.failUnless(iURLiP('http://www.foobar.com/bar/foo'))
        self.failIf(iURLiP('http://www.foobar.com/bar2/foo'))
        self.failUnless(iURLiP('https://www.foobar.com/bar/foo/folder'))
        self.failIf(iURLiP('http://www.foobar.com:8080/bar/foo/folder'))
        self.failIf(iURLiP('http://www.foobar.com/bar'))
        self.failIf(iURLiP('/images'))
        self.failUnless(iURLiP('/bar/foo/foo'))

    def test_isURLInPortalRelative(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal
        #non-root relative urls will need a current context to be passed in
        self.failUnless(iURLiP(
                               'images/img1.jpg'))
        self.failUnless(iURLiP(
                               './images/img1.jpg'))
        self.failUnless(iURLiP( #/bar/foo/something
                               '../something', self.site.foo.doc1))
        self.failIf(iURLiP( #/bar/afolder
                           '../../afolder', self.site.foo.doc1))
        self.failIf(iURLiP( #/afolder
                           '../../../afolder', self.site.foo.doc1))
        self.failIf(iURLiP( #/../afolder? How do we have more ../'s than there are parts in the URL?
                           '../../../../afolder', self.site.foo.doc1))
        self.failUnless(iURLiP( #/bar/foo/afolder
                               '../../foo/afolder', self.site.foo.doc1))

    def test_isURLInPortalExternal(self):
        url_tool = self._makeOne()
        iURLiP = url_tool.isURLInPortal
        self.failUnless(iURLiP('http://external1'))
        self.failUnless(iURLiP('http://external1/'))
        self.failUnless(iURLiP('http://external1/something'))
        self.failUnless(iURLiP('http://external2'))
        self.failUnless(iURLiP('http://external2/'))
        self.failUnless(iURLiP('http://external2/something'))
        self.failUnless(iURLiP('http://external3/site'))
        self.failUnless(iURLiP('http://external3/site/'))
        self.failUnless(iURLiP('http://external3/site/something'))
        self.failUnless(iURLiP('http://external4/site'))
        self.failUnless(iURLiP('http://external4/site/'))
        self.failUnless(iURLiP('http://external4/site/something'))

        self.failIf(iURLiP('http://external3/other'))
        self.failIf(iURLiP('http://external4/other'))
        self.failIf(iURLiP('http://external5'))
        self.failIf(iURLiP('http://external11'))
