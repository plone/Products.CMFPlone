import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.utils import getToolByName

from webdav.NullResource import NullResource
from Acquisition import aq_base
from StringIO import StringIO


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


class TestDAVMetadata(PloneTestCase.FunctionalTestCase):
    # Confirms fix for http://plone.org/collector/3217
    # The fix itself is in CMFDefault.Document, not Plone.

    html = """\
<html>
<head><title>Foo</title></head>
<body>Bar</body>
</html>
"""

    def afterSetUp(self):
        self.basic_auth = '%s:secret' % PloneTestCase.default_user
        self.folder_path = self.folder.absolute_url(1)

    def testDocumentMetadata(self):
        response = self.publish(self.folder_path+'/doc',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(self.html),
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 201)
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
        self.assertEqual(doc.Language(), '')
        self.assertEqual(doc.Rights(), '')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDAVProperties))
    suite.addTest(makeSuite(TestDAVMetadata))
    return suite

if __name__ == '__main__':
    framework()
