import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.utils import getToolByName

from webdav.NullResource import NullResource
from Acquisition import aq_base

import base64
auth_info = 'Basic %s' % base64.encodestring('%s:secret' % PloneTestCase.default_user)

def mkdict(items):
    '''Constructs a dict from a sequence of (key, value) pairs.'''
    d = {}
    for k, v in items:
        d[k] = v
    return d


class TestDAVProperties(PloneTestCase.PloneTestCase):

    def testPropertiesToolTitle(self):
        ptool = getToolByName(self.portal, 'portal_properties')
        psets = mkdict(ptool.propertysheets.items())
        self.failUnless('default' in psets.keys())
        default = psets['default']
        items = mkdict(default.propertyItems())
        self.failUnless('title' in items.keys())
        self.assertEquals(items['title'], self.portal.title)


class TestDAVMetadata(PloneTestCase.PloneTestCase):
    # Confirms fix for http://plone.org/collector/3217
    # The fix itself is in CMFDefault.Document, not Plone.

    html = """\
<html>
<head><title>Foo</title></head>
<body>Bar</body>
</html>
"""

    def afterSetUp(self):
        request = self.app.REQUEST
        request['PARENTS'] = [self.folder, self.portal, self.app]
        # Fake a PUT request
        request['BODY'] = self.html
        request.environ['CONTENT_TYPE'] = 'text/html'
        request.environ['REQUEST_METHOD'] = 'PUT'
        request._auth = auth_info
        request.RESPONSE._auth = 1
        request.maybe_webdav_client = 1
        # PUT a document
        new = NullResource(self.folder, 'doc', request).__of__(self.folder)
        new.PUT(request, request.RESPONSE)

    def testDocumentMetadata(self):
        doc = self.folder.doc
        self.assertEqual(doc.Title(), 'Foo')
        self.assertEqual(doc.EditableBody(), 'Bar')
        self.assertEqual(doc.Format(), 'text/html')
        # Remaining elements should contain the defaults
        self.assertEqual(doc.Description(), '')
        self.assertEqual(doc.Subject(), ())
        self.assertEqual(doc.Contributors(), ())
        self.assertEqual(doc.EffectiveDate(), 'None')
        self.assertEqual(doc.ExpirationDate(), 'None')
        self.assertEqual(doc.Language(), 'en')
        self.assertEqual(doc.Rights(), '')


def test_suite():
    from unittest import TestSuite, makeSuite
    from Testing.ZopeTestCase.doctest import FunctionalDocFileSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestDAVProperties))
    suite.addTest(makeSuite(TestDAVMetadata))

    suite.addTest(FunctionalDocFileSuite('dav/index_html_put.txt',
                                package='Products.CMFPlone.tests',
                                test_class=PloneTestCase.FunctionalTestCase))
    return suite

if __name__ == '__main__':
    framework()
