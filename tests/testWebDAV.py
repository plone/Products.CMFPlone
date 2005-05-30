import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from cStringIO import StringIO
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy
from Products.CMFCore.utils import getToolByName

from webdav.NullResource import NullResource
from Acquisition import aq_base
from StringIO import StringIO


default_user = ZopeTestCase.user_name
default_password = ZopeTestCase.user_password

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
        self.basic_auth = '%s:secret' % PloneTestCase.default_user
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
        self.assertEqual(self.folder.new_html.EditableBody(), 'Bar')
        self.assertEqual(self.folder.new_html.portal_type, 'Document')

    def testPUTIndexHtmlDocument(self):
        # Create an index_html document via FTP/DAV
        response = self.publish(self.folder_path+'/index_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201, response.getBody())
        self.failUnless('index_html' in self.folder.objectIds())
        self.assertEqual(self.folder.index_html.EditableBody(), 'Bar')
        self.assertEqual(self.folder._getOb('index_html').EditableBody(), 'Bar')
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
        self.assertEqual(str(self.folder.new_image.data), dummy.GIF)
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
        self.assertEqual(str(self.folder.index_html.data), dummy.GIF)
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
        self.assertEqual(self.portal.new_html.EditableBody(), 'Bar')
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
        self.assertEqual(self.portal.index_html.EditableBody(), 'Bar')
        self.assertEqual(self.portal._getOb('index_html').EditableBody(), 'Bar')
        self.assertEqual(self.portal.index_html.portal_type, 'Document')

class TestDAVOperations(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.loginPortalOwner()
        self.basic_auth = '%s:%s' % (PloneTestCase.portal_owner, '')
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def test_document_propfind_index_html_non_exist_folder(self):
        self.folder.invokeFactory('Folder', 'sub')
        self.failIf('index_html' in self.folder.sub.objectIds())

        # Do a PROPFIND on folder/index_html, this needs to result in a NotFound.
        response = self.publish(self.folder_path + '/sub/index_html',
                                env={},
                                request_method='PROPFIND',
                                stdin=StringIO(''),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_document_propfind_index_html_exist_folder(self):
        self.folder.invokeFactory('Folder', 'sub')
        self.folder.sub.invokeFactory('Document', 'index_html')
        self.failUnless('index_html' in self.folder.sub.objectIds())

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(self.folder_path + '/sub/index_html',
                                env={},
                                request_method='PROPFIND',
                                stdin=StringIO(''),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_document_propfind_index_html_non_exist_portal(self):
        if 'index_html' in self.portal.objectIds():
            self.portal.manage_delObjects('index_html')

        self.failIf('index_html' in self.portal.objectIds())

        # Do a PROPFIND on portal/index_html, this needs to result in a NotFound.
        response = self.publish(self.portal_path + '/index_html',
                                env={},
                                request_method='PROPFIND',
                                stdin=StringIO(''),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_document_propfind_index_html_exist_portal(self):
        if 'index_html' not in self.portal.objectIds():
            self.portal.invokeFactory('Document', 'index_html')

        self.failUnless('index_html' in self.portal.objectIds())

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(self.portal_path + '/index_html',
                                env={},
                                request_method='PROPFIND',
                                stdin=StringIO(''),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDAVProperties))
    suite.addTest(makeSuite(TestDAVMetadata))
    suite.addTest(makeSuite(TestPUTObjects))
    suite.addTest(makeSuite(TestDAVOperations))
    return suite

if __name__ == '__main__':
    framework()
