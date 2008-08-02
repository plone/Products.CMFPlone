#
# Tests the workflow tool
#

from Products.CMFPlone.tests import PloneTestCase

portal_name = PloneTestCase.portal_name


class TestURLTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.url = self.portal.portal_url
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.foo.invokeFactory('Document', id='doc1')
        
    def test_isURLInPortal(self):
        iURLiP = self.url.isURLInPortal
        self.failUnless(iURLiP(
                               'http://nohost/%s/foo' % portal_name))
        self.failUnless(iURLiP(
                               'http://nohost/%s' % portal_name))
        self.failIf(iURLiP(
                           'http://nohost2/%s/foo' % portal_name))
        self.failUnless(iURLiP(
                               'https://nohost/%s/bar' % portal_name))
        self.failIf(iURLiP(
                           'http://nohost:8080/%s/baz' % portal_name))
        self.failIf(iURLiP(
                           'http://nohost/'))
        self.failIf(iURLiP(
                           '/images'))
        self.failUnless(iURLiP(
                               '/%s/foo' % portal_name))
    
    def test_isURLInPortalRelative(self):
        iURLiP = self.url.isURLInPortal
        #non-root relative urls will need a current context to be passed in
        self.failUnless(iURLiP(
                               'images/img1.jpg'))
        self.failUnless(iURLiP(
                               './images/img1.jpg'))
        self.failUnless(iURLiP( #/plone/Members/test_user_1_/something
                               '../something', self.folder.foo.doc1))
        self.failUnless(iURLiP( #/plone/Members/afolder
                               '../../afolder', self.folder.foo.doc1))
        self.failUnless(iURLiP( #/plone/afolder
                               '../../../afolder', self.folder.foo.doc1))
        self.failIf(iURLiP( #/afolder
                           '../../../../afolder', self.folder.foo.doc1))
        self.failIf(iURLiP( #/../afolder? How do we have more ../'s than there are parts in the URL?
                           '../../../../../afolder', self.folder.foo.doc1))
        self.failUnless(iURLiP( #/plone/afolder
                               '../../../../%s/afolder' % portal_name ,self.folder.foo.doc1))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestURLTool))
    return suite
