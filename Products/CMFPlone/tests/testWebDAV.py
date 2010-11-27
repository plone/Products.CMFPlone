
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests.PloneTestCase import default_user
from Products.CMFPlone.tests.PloneTestCase import default_password

from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

html = """\
<html>
<head><title>Foo</title></head>
<body>Bar</body>
</html>
"""


class TestDAVProperties(PloneTestCase.PloneTestCase):

    def testPropertiesToolTitle(self):
        ptool = getToolByName(self.portal, 'portal_properties')
        psets = dict(ptool.propertysheets.items())
        self.failUnless('webdav' in psets.keys())
        default = psets['webdav']
        items = dict(default.propertyItems())
        self.failUnless('displayname' in items.keys())
        self.assertEquals(items['displayname'], ptool.title)


class TestDAVMetadata(PloneTestCase.FunctionalTestCase):
    # Confirms fix for http://dev.plone.org/plone/ticket/3217
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
    # Confirms fix for http://dev.plone.org/plone/ticket/1375

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
        self.failUnless('new_html' in self.folder)
        self.assertEqual(self.folder.new_html.portal_type, 'Document')
        self.assertEqual(self.folder.new_html.EditableBody(), html)

    def testPUTTextDocumentRSTNoContentType(self):
        # Create a new document via FTP/DAV, some clients do not send
        # a proper Content-Type header.
        response = self.publish(self.folder_path+'/test.rst',
                                env={'CONTENT_LENGTH':'0'},
                                request_method='PUT',
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.rst' in self.folder)
        self.assertEqual(self.folder['test.rst'].portal_type, 'Document')
        self.assertEqual(self.folder['test.rst'].EditableBody(), '')

    def testPUTTextDocumentTXTNoContentType(self):
        # Create a new document via FTP/DAV, some clients do not send
        # a proper Content-Type header.
        response = self.publish(self.folder_path+'/test.txt',
                                env={'CONTENT_LENGTH':'0'},
                                request_method='PUT',
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.txt' in self.folder)
        self.assertEqual(self.folder['test.txt'].portal_type, 'Document')
        self.assertEqual(self.folder['test.txt'].EditableBody(), '')

    def testPUTTextDocumentININoContentType(self):
        # Create a new document via FTP/DAV, some clients do not send
        # a proper Content-Type header.
        response = self.publish(self.folder_path+'/test.ini',
                                env={'CONTENT_LENGTH':'0'},
                                request_method='PUT',
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.ini' in self.folder)
        self.assertEqual(self.folder['test.ini'].portal_type, 'Document')
        self.assertEqual(self.folder['test.ini'].EditableBody(), '')

    def testPUTIndexHtmlDocument(self):
        # Create an index_html document via FTP/DAV
        response = self.publish(self.folder_path+'/index_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('index_html' in self.folder)
        self.assertEqual(self.folder.index_html.portal_type, 'Document')
        self.assertEqual(self.folder.index_html.EditableBody(), html)
        self.assertEqual(self.folder._getOb('index_html').EditableBody(), html)

    def testPUTImage(self):
        # Create a new image via FTP/DAV
        response = self.publish(self.folder_path+'/new_image',
                                env={'CONTENT_TYPE': 'image/gif'},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('new_image' in self.folder)
        self.assertEqual(self.folder.new_image.portal_type, 'Image')
        self.assertEqual(str(self.folder.new_image.getImage().data), dummy.GIF)

    def testPUTImageGIFNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(self.folder_path+'/test.gif',
                                env={'CONTENT_LENGTH':len(dummy.GIF)},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.gif' in self.folder)
        self.assertEqual(self.folder['test.gif'].portal_type, 'Image')
        self.assertEqual(str(self.folder['test.gif'].getImage().data), dummy.GIF)

    def testPUTImageJPGNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(self.folder_path+'/test.jpg',
                                env={'CONTENT_LENGTH':len(dummy.GIF)},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.jpg' in self.folder)
        self.assertEqual(self.folder['test.jpg'].portal_type, 'Image')
        self.assertEqual(str(self.folder['test.jpg'].getImage().data), dummy.GIF)

    def testPUTImagePNGNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(self.folder_path+'/test.png',
                                env={'CONTENT_LENGTH':len(dummy.GIF)},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.png' in self.folder)
        self.assertEqual(self.folder['test.png'].portal_type, 'Image')
        self.assertEqual(str(self.folder['test.png'].getImage().data), dummy.GIF)

    def testPUTImageTIFFNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(self.folder_path+'/test.tiff',
                                env={'CONTENT_LENGTH':len(dummy.GIF)},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.tiff' in self.folder)
        self.assertEqual(self.folder['test.tiff'].portal_type, 'Image')
        self.assertEqual(str(self.folder['test.tiff'].getImage().data), dummy.GIF)

    def testPUTImageICONoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(self.folder_path+'/test.ico',
                                env={'CONTENT_LENGTH':len(dummy.GIF)},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('test.ico' in self.folder)
        self.assertEqual(
            self.folder['test.ico'].portal_type, 'Image',
            'If you are on a Mac and this fails, please see: http://plone.org/documentation/error/unittest to fix.')
        self.assertEqual(str(self.folder['test.ico'].getImage().data), dummy.GIF)

    def testPUTIndexHtmlImage(self):
        # Create a new image named index_html via FTP/DAV
        response = self.publish(self.folder_path+'/index_html',
                                env={'CONTENT_TYPE': 'image/gif'},
                                request_method='PUT',
                                stdin=StringIO(dummy.GIF),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('index_html' in self.folder)
        self.assertEqual(self.folder.index_html.portal_type, 'Image')
        self.assertEqual(str(self.folder.index_html.getImage().data), dummy.GIF)

    def testPUTDocumentIntoPortal(self):
        # Create a new document in the portal via FTP/DAV
        self.setRoles(['Manager'])

        response = self.publish(self.portal_path+'/new_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('new_html' in self.portal)
        self.assertEqual(self.portal.new_html.portal_type, 'Document')
        self.assertEqual(self.portal.new_html.EditableBody(), html)

    def testPUTIndexHtmlDocumentIntoPortal(self):
        # Create an index_html document in the portal via FTP/DAV
        self.setRoles(['Manager'])

        response = self.publish(self.portal_path+'/index_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('index_html' in self.portal)
        self.assertEqual(self.portal.index_html.portal_type, 'Document')
        self.assertEqual(self.portal.index_html.EditableBody(), html)
        self.assertEqual(self.portal._getOb('index_html').EditableBody(), html)


class TestDAVOperations(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.basic_auth = '%s:%s' % (PloneTestCase.portal_owner, PloneTestCase.default_password)
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def test_document_propfind_index_html_exist_folder(self):
        self.folder.invokeFactory('Folder', 'sub')
        self.folder.sub.invokeFactory('Document', 'index_html')
        self.failUnless('index_html' in self.folder.sub)

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(self.folder_path + '/sub/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_document_propfind_index_html_non_exist_folder(self):
        self.folder.invokeFactory('Folder', 'sub')
        self.failIf('index_html' in self.folder.sub)

        # Do a PROPFIND on folder/index_html, this needs to result in a NotFound.
        response = self.publish(self.folder_path + '/sub/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_document_propfind_index_html_exist_portal(self):
        if 'index_html' not in self.portal:
            self.portal.invokeFactory('Document', 'index_html')

        self.failUnless('index_html' in self.portal)

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(self.portal_path + '/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_document_propfind_index_html_non_exist_portal(self):
        if 'index_html' in self.portal:
            self.portal.manage_delObjects('index_html')

        self.failIf('index_html' in self.portal)

        # Do a PROPFIND on portal/index_html, this needs to result in a NotFound.
        response = self.publish(self.portal_path + '/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_propfind_portal_root_index_html_exists(self):
        if 'index_html' not in self.portal:
            self.portal.invokeFactory('Document', 'index_html')

        self.failUnless('index_html' in self.portal)

        # Do a PROPFIND on portal, this needs to result in a 207
        response = self.publish(self.portal_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_portal_root_index_html_not_exists(self):
        if 'index_html' in self.portal:
            self.portal.manage_delObjects('index_html')

        self.failIf('index_html' in self.portal)

        # Do a PROPFIND on portal, this needs to result in a 207
        response = self.publish(self.portal_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_folder_index_html_exists(self):
        if 'index_html' not in self.folder:
            self.folder.invokeFactory('Document', 'index_html')

        self.failUnless('index_html' in self.folder)

        # Do a PROPFIND on folder, this needs to result in a 207
        response = self.publish(self.folder_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_folder_index_html_not_exists(self):
        if 'index_html' in self.folder:
            self.folder.manage_delObjects('index_html')

        self.failIf('index_html' in self.folder)

        # Do a PROPFIND on folder, this needs to result in a 207
        response = self.publish(self.folder_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())


def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestDAVProperties))
    # DISABLED the metadata test, this is not yet implemented in ATCT
    ##suite.addTest(makeSuite(TestDAVMetadata))
    suite.addTest(makeSuite(TestPUTObjects))
    suite.addTest(makeSuite(TestDAVOperations))
    return suite
