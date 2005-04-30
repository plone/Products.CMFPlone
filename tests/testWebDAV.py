import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests.PloneTestCase import default_user
from Products.CMFPlone.tests.PloneTestCase import default_password
from Products.CMFCore.utils import getToolByName

from webdav.NullResource import NullResource
from Acquisition import aq_base
from StringIO import StringIO

html = """\
<html>
<head><title>Foo</title></head>
<body>Bar</body>
</html>
"""

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

    def afterSetUp(self):
        self.basic_auth = '%s:%s' % (default_user, default_password)
        self.folder_path = self.folder.absolute_url(1)

    def testDocumentMetadata(self):
        response = self.publish(self.folder_path+'/doc',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
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


class TestPUTObjects(PloneTestCase.FunctionalTestCase):
    # PUT objects into Plone including special cases like index_html.
    # Confirms fix for http://plone.org/collector/1375

    def afterSetUp(self):
        self.basic_auth = '%s:%s' % (default_user, default_password)
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def testPUTDocument(self):
        # Create a new document via FTP/DAV
        response = self.publish(self.folder_path+'/new_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('new_html' in self.folder.objectIds())
        self.assertEqual(self.folder.new_html.EditableBody(), html)
        self.assertEqual(self.folder.new_html.portal_type, 'Document')

    def testPUTIndexHtmlDocument(self):
        # Create an index_html document via FTP/DAV
        response = self.publish(self.folder_path+'/index_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('index_html' in self.folder.objectIds())
        self.assertEqual(self.folder.index_html.EditableBody(), html)
        self.assertEqual(self.folder._getOb('index_html').EditableBody(), html)
        self.assertEqual(self.folder.index_html.portal_type, 'Document')

    def testPUTImage(self):
        # Create a new image via FTP/DAV
        response = self.publish(self.folder_path+'/new_image',
                                env={'CONTENT_TYPE': 'image/gif'},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('new_image' in self.folder.objectIds())
        self.assertEqual(str(self.folder.new_image.getImage().data), dummy.GIF)
        self.assertEqual(self.folder.new_image.portal_type, 'Image')

    def testPUTIndexHtmlImage(self):
        # Create a new image named index_html via FTP/DAV
        response = self.publish(self.folder_path+'/index_html',
                                env={'CONTENT_TYPE': 'image/gif'},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('index_html' in self.folder.objectIds())
        self.assertEqual(str(self.folder.index_html.getImage().data), dummy.GIF)
        self.assertEqual(self.folder.index_html.portal_type, 'Image')

    def testPUTDocumentIntoPortal(self):
        # Create a new document in the portal via FTP/DAV
        self.setRoles(['Manager'])

        response = self.publish(self.portal_path+'/new_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('new_html' in self.portal.objectIds())
        self.assertEqual(self.portal.new_html.EditableBody(), html)
        self.assertEqual(self.portal.new_html.portal_type, 'Document')

    def testPUTIndexHtmlDocumentIntoPortal(self):
        # Create an index_html document in the portal via FTP/DAV
        self.setRoles(['Manager'])

        response = self.publish(self.portal_path+'/index_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('index_html' in self.portal.objectIds())
        self.assertEqual(self.portal.index_html.EditableBody(), html)
        self.assertEqual(self.portal._getOb('index_html').EditableBody(), html)
        self.assertEqual(self.portal.index_html.portal_type, 'Document')


def test_suite():
    from unittest import TestSuite, makeSuite
    from Testing.ZopeTestCase import FunctionalDocFileSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestDAVProperties))
    # DISABLED the metadata test, this is not yet implemented in ATCT
    ##suite.addTest(makeSuite(TestDAVMetadata))
    suite.addTest(makeSuite(TestPUTObjects))

    # This, ladies and gentlemen, is a functional *doctest*:
    suite.addTest(FunctionalDocFileSuite('dav/index_html_put.txt',
                                package='Products.CMFPlone.tests',
                                test_class=PloneTestCase.FunctionalTestCase))

    return suite

if __name__ == '__main__':
    framework()
