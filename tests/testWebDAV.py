from StringIO import StringIO
from DateTime import DateTime

from AccessControl import getSecurityManager
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests.PloneTestCase import default_user
from Products.CMFPlone.tests.PloneTestCase import default_password
from Products.CMFPlone.ContentTypeRegistry import DelegatingContentTypeRegistry
from Products.CMFCore.utils import getToolByName

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
        self.assertEquals(items['displayname'], self.portal.title)


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
        self.failUnless('new_html' in self.folder.objectIds())
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
        self.failUnless('test.rst' in self.folder.objectIds())
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
        self.failUnless('test.txt' in self.folder.objectIds())
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
        self.failUnless('test.ini' in self.folder.objectIds())
        self.assertEqual(self.folder['test.ini'].portal_type, 'File')

    def testPUTIndexHtmlDocument(self):
        # Create an index_html document via FTP/DAV
        response = self.publish(self.folder_path+'/index_html',
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless('index_html' in self.folder.objectIds())
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
        self.failUnless('new_image' in self.folder.objectIds())
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
        self.failUnless('test.gif' in self.folder.objectIds())
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
        self.failUnless('test.jpg' in self.folder.objectIds())
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
        self.failUnless('test.png' in self.folder.objectIds())
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
        self.failUnless('test.tiff' in self.folder.objectIds())
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
        self.failUnless('test.ico' in self.folder.objectIds())
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
        self.failUnless('index_html' in self.folder.objectIds())
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
        self.failUnless('new_html' in self.portal.objectIds())
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
        self.failUnless('index_html' in self.portal.objectIds())
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
        self.failUnless('index_html' in self.folder.sub.objectIds())

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(self.folder_path + '/sub/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_document_propfind_index_html_non_exist_folder(self):
        self.folder.invokeFactory('Folder', 'sub')
        self.failIf('index_html' in self.folder.sub.objectIds())

        # Do a PROPFIND on folder/index_html, this needs to result in a NotFound.
        response = self.publish(self.folder_path + '/sub/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_document_propfind_index_html_exist_portal(self):
        if 'index_html' not in self.portal.objectIds():
            self.portal.invokeFactory('Document', 'index_html')

        self.failUnless('index_html' in self.portal.objectIds())

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(self.portal_path + '/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_document_propfind_index_html_non_exist_portal(self):
        if 'index_html' in self.portal.objectIds():
            self.portal.manage_delObjects('index_html')

        self.failIf('index_html' in self.portal.objectIds())

        # Do a PROPFIND on portal/index_html, this needs to result in a NotFound.
        response = self.publish(self.portal_path + '/index_html',
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_propfind_portal_root_index_html_exists(self):
        if 'index_html' not in self.portal.objectIds():
            self.portal.invokeFactory('Document', 'index_html')

        self.failUnless('index_html' in self.portal.objectIds())

        # Do a PROPFIND on portal, this needs to result in a 207
        response = self.publish(self.portal_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_portal_root_index_html_not_exists(self):
        if 'index_html' in self.portal.objectIds():
            self.portal.manage_delObjects('index_html')

        self.failIf('index_html' in self.portal.objectIds())

        # Do a PROPFIND on portal, this needs to result in a 207
        response = self.publish(self.portal_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_folder_index_html_exists(self):
        if 'index_html' not in self.folder.objectIds():
            self.folder.invokeFactory('Document', 'index_html')

        self.failUnless('index_html' in self.folder.objectIds())

        # Do a PROPFIND on folder, this needs to result in a 207
        response = self.publish(self.folder_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_folder_index_html_not_exists(self):
        if 'index_html' in self.folder.objectIds():
            self.folder.manage_delObjects('index_html')

        self.failIf('index_html' in self.folder.objectIds())

        # Do a PROPFIND on folder, this needs to result in a 207
        response = self.publish(self.folder_path,
                                request_method='PROPFIND',
                                env={'HTTP_DEPTH': '0'},
                                stdin=StringIO(),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_member_mkcol_sets_title(self):
        name = 'Some Random Folder'
        response = self.publish(self.folder_path + '/' + name,
                                request_method='MKCOL',
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 201)
        obj = self.folder._getOb(name)
        self.assertEquals(obj.Title(), name)

    def test_member_can_lock_and_unlock(self):
        name = 'some-object'
        response = self.publish(self.folder_path + '/' + name,
                                request_method='PUT',
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 201)
        obj = self.folder._getOb(name)
        self.assertEquals(obj.Title(), name)

        lock = """
        <?xml version="1.0" encoding="utf-8"?>
        <lockinfo xmlns='DAV:'>
        <lockscope><exclusive/></lockscope>
        <locktype><write/></locktype>
        <owner>%s</owner></lockinfo>
        """ % default_user

        lock = ''.join([l.strip() for l in lock.splitlines() if l.strip()])

        response = self.publish(self.folder_path + '/' + name,
                                request_method='LOCK',
                                stdin=StringIO(lock),
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 200)

        token = self.folder._getOb(name).wl_lockValues()[0].getLockToken()
        response = self.publish(self.folder_path + '/' + name,
                                request_method='UNLOCK',
                                env={'HTTP_LOCK_TOKEN':
                                     '<opaquelocktoken:%s>' % token},
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 204)
        self.failIf(self.folder._getOb(name).wl_lockValues())

class TestContentTypeRegistry(PloneTestCase.FunctionalTestCase):
    # Check that the default settings for the content type registry
    # create sane content objects.

    def afterSetUp(self):
        self.basic_auth = '%s:%s' % (default_user, default_password)
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def testPUTNewsItem(self):
        name = 'news_item.news'
        title = name
        portal_type = 'News Item'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTLink_ext_link(self):
        name = 'new_link.link'
        title = name
        portal_type = 'Link'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTLink_ext_url(self):
        name = 'new_link.url'
        title = name
        portal_type = 'Link'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTLink_ext_desktop(self):
        name = 'new_link.desktop'
        title = name
        portal_type = 'Link'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTEvent_ext_event(self):
        name = 'new_event.event'
        title = name
        portal_type = 'Event'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTEvent_ext_evt(self):
        name = 'new_event.evt'
        title = name
        portal_type = 'Event'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTFolder_ext_ics(self):
        name = 'new_event.ics'
        title = name
        portal_type = 'Folder'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), '') # XXX TODO, title from filename

    def testPUTFavorite_ext_fav(self):
        name = 'new_favorite.fav'
        title = name
        portal_type = 'Favorite'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_txt(self):
        name = 'new_document.txt'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_stx(self):
        name = 'new_document.stx'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_rst(self):
        name = 'new_document.rst'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_rest(self):
        name = 'new_document.rest'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_py(self):
        name = 'new_document.py'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_htm(self):
        name = 'new_document.htm'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_html(self):
        name = 'new_document.html'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_ext_xml(self):
        name = 'new_document.xml'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_ext_jpg(self):
        name = 'new_image.jpg'
        title = name
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_ext_jpeg(self):
        name = 'new_image.jpeg'
        title = name
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_ext_png(self):
        name = 'new_image.png'
        title = name
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_ext_gif(self):
        name = 'new_image.gif'
        title = name
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_ext_ico(self):
        name = 'new_image.ico'
        title = name
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_ext_bmp(self):
        name = 'new_image.bmp'
        title = name
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_mime_image_jpg(self):
        name = 'new_image'
        title = name
        mime_type = 'image/jpg'
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_mime_image_jpeg(self):
        name = 'new_image'
        title = name
        mime_type = 'image/jpeg'
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_mime_image_png(self):
        name = 'new_image'
        title = name
        mime_type = 'image/png'
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_mime_image_gif(self):
        name = 'new_image'
        title = name
        mime_type = 'image/gif'
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_mime_image_ico(self):
        name = 'new_image'
        title = name
        mime_type = 'image/ico'
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTImage_mime_image_bmp(self):
        name = 'new_image'
        title = name
        mime_type = 'image/bmp'
        portal_type = 'Image'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_mime_application_xhtml(self):
        name = 'new_document'
        title = name
        mime_type = 'application/xhtml+xml'
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_mime_message_rfc822(self):
        name = 'new_document'
        title = name
        mime_type = 'message/rfc822'
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTLink_mime_text_xurl(self):
        name = 'new_link'
        title = name
        mime_type = 'text/x-url'
        portal_type = 'Link'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_mime_text(self):
        name = 'new_document'
        title = name
        mime_type = 'text/plain'
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTLink_mime_application_xdesktop(self):
        name = 'new_link'
        title = name
        mime_type = 'application/x-desktop'
        portal_type = 'Link'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTDocument_mime_application_xml(self):
        name = 'new_document'
        title = name
        mime_type = 'application/xml'
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTFile_mime_application(self):
        name = 'new_file'
        title = name
        mime_type = 'application/octet-stream'
        portal_type = 'File'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTFile_mime_audio(self):
        name = 'new_file'
        title = name
        mime_type = 'audio/mpeg'
        portal_type = 'File'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTFile_mime_audio(self):
        name = 'new_file'
        title = name
        mime_type = 'audio/mpeg'
        portal_type = 'File'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTFile_mime_video(self):
        name = 'new_file'
        title = name
        mime_type = 'video/mpeg'
        portal_type = 'File'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': mime_type},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTFile_mime_text_unknown(self):
        name = 'new_file'
        title = name
        portal_type = 'File'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            env={'CONTENT_TYPE': 'text/x-unknown-content-type'},
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTFile_catch_all(self):
        name = 'new_file.yyk'
        title = name
        portal_type = 'File'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

    def testPUTNewsItem_override(self):
        # It is possible to override the default rules for the
        # content_type_registry on a folder-by-folder basis by adding
        # a 'Delegating Content Type Registry'.
        name = 'news_item1.txt'
        title = name
        portal_type = 'Document'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

        # Now create a 'Delegating Content Type Registry' and add a
        # rule mapping from .txt -> News Item and try again.
        # 
        # Note you must be Manager to do this, otherwise the
        # _checkId() method from PortalFolder will not allow you to
        # override a tool that is present on the portal root.

        roles = getSecurityManager().getUser().getRoles()
        self.setRoles(['Manager'])
        
        add_tool = self.folder.manage_addProduct['CMFPlone'].manage_addTool
        add_tool(DelegatingContentTypeRegistry.meta_type)

        tool = self.folder._getOb('content_type_registry')        
        tool.addPredicate('news_override', 'extension')
        tool.getPredicate('news_override').edit('txt')
        tool.assignTypeName('news_override', 'News Item')
        tool.reorderPredicate('news_override', 0)
        
        self.setRoles(roles)
        
        name = 'news_item2.txt'
        title = name
        portal_type = 'News Item'
        response = self.publish(
            self.folder_path + '/' + name,
            request_method='PUT',
            stdin=StringIO(),
            basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, portal_type)
        self.assertEqual(obj.Title(), title)

        # Make sure that original settings from the default
        # content_type_registry still apply to this folder.
        self.testPUTImage_mime_image_bmp()
        self.testPUTDocument_mime_message_rfc822()

class TestPUTDefaultPage(PloneTestCase.FunctionalTestCase):
    # PUT a file which matches the 'default_page' configuration in
    # site properties does set the object as the default page for a
    # folder.
    
    def afterSetUp(self):
        self.basic_auth = '%s:%s' % (default_user, default_password)
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def testPUTDefaultPageIndexHtml1(self):
        # Create an index_html document via FTP/DAV sets it as the
        # default page for the folder.
        name = 'index_html'
        response = self.publish(self.folder_path + '/' + name,
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        self.assertEqual(self.folder._getOb(name).portal_type, 'Document')
        self.assertEqual(self.folder.getDefaultPage(), name)

    def testPUTDefaultPageIndexHtml2(self):
        # Create an index_html document via FTP/DAV sets it as the
        # default page for the folder.
        name = 'index.html'
        response = self.publish(self.folder_path + '/' + name,
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        self.assertEqual(self.folder._getOb(name).portal_type, 'Document')
        self.assertEqual(self.folder.getDefaultPage(), name)

    def testPUTDefaultPageIndexHtm(self):
        # Create an index_html document via FTP/DAV sets it as the
        # default page for the folder.
        name = 'index.htm'
        response = self.publish(self.folder_path + '/' + name,
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        self.assertEqual(self.folder._getOb(name).portal_type, 'Document')
        self.assertEqual(self.folder.getDefaultPage(), name)

    def testPUTDefaultPageFrontPage(self):
        # Create an index_html document via FTP/DAV sets it as the
        # default page for the folder.
        name = 'FrontPage'
        response = self.publish(self.folder_path + '/' + name,
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(html),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        self.assertEqual(self.folder._getOb(name).portal_type, 'Document')
        self.assertEqual(self.folder.getDefaultPage(), name)

class TestPUTDefaultMarshaller(PloneTestCase.FunctionalTestCase):
    # Check for the default marshaller implementation that gets used
    # for a certain content object is sane.
    
    def afterSetUp(self):
        self.basic_auth = '%s:%s' % (default_user, default_password)
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def testPUTLinkDefaultMarshallerURL(self):
        link = '\n'.join([
        "[InternetShortcut]", 
        "URL=http://www.google.com/ig",
        "Modified=F0DD16921EE9C50142",
        ])
        name = 'google.url'
        response = self.publish(self.folder_path + '/' + name,
                                request_method='PUT',
                                stdin=StringIO(link),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, 'Link')
        self.assertEqual(obj.getRemoteUrl(), 'http://www.google.com/ig')


        response = self.publish(self.folder_path + '/' + name +
                                '/manage_DAVget',
                                request_method='GET',
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.failUnless('[InternetShortcut]' in body, body)
        self.failUnless('URL' in body, body)
        self.failUnless('http://www.google.com/ig' in body, body)

    def testPUTLinkDefaultMarshallerDesktop(self):
        link = '\n'.join([
            "[Desktop Entry]",
            "Version=1.0",
            "Encoding=UTF-8",
            "Name=Google",
            "Type=Link",
            "URL=http://www.google.com/ig",
            "TryExec=",
            "Icon=/usr/share/pixmaps/firefox.xpm",
            "X-GNOME-DocPath=",
            "Terminal=false",
            "GenericName[en]=Google Website",
            "Comment[en]=Launch Google Website",
            ])
        name = 'google.desktop'
        response = self.publish(self.folder_path + '/' + name,
                                env={'CONTENT_TYPE': 'text/html'},
                                request_method='PUT',
                                stdin=StringIO(link),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, 'Link')
        self.assertEqual(obj.getRemoteUrl(), 'http://www.google.com/ig')

        response = self.publish(self.folder_path + '/' + name +
                                '/manage_DAVget',
                                request_method='GET',
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        # XXX Can't decide which format is right when
        # marshalling. Maybe should serialize both?
        
        # self.failUnless('[Desktop Entry]' in body, body)
        self.failUnless('URL' in body, body)
        self.failUnless('http://www.google.com/ig' in body, body)

    def testPUTEventDefaultMarshaller(self):
        event = '\n'.join([
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "X-WR-CALNAME:Music",
            "PRODID:-//Apple Computer\, Inc//iCal 2.0//EN",
            "X-WR-RELCALID:4BA6B8FF-8A11-40E4-8671-63F56155E2B8",
            "X-WR-TIMEZONE:US/Eastern",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VTIMEZONE",
            "TZID:US/Eastern",
            "LAST-MODIFIED:20051104T175952Z",
            "BEGIN:DAYLIGHT",
            "DTSTART:20050403T070000",
            "TZOFFSETTO:-0400",
            "TZOFFSETFROM:+0000",
            "TZNAME:EDT",
            "END:DAYLIGHT",
            "BEGIN:STANDARD",
            "DTSTART:20051030T020000",
            "TZOFFSETTO:-0500",
            "TZOFFSETFROM:-0400",
            "TZNAME:EST",
            "END:STANDARD",
            "BEGIN:DAYLIGHT",
            "DTSTART:20060402T010000",
            "TZOFFSETTO:-0400",
            "TZOFFSETFROM:-0500",
            "TZNAME:EDT",
            "END:DAYLIGHT",
            "END:VTIMEZONE",
            "BEGIN:VEVENT",
            "CLASS:PUBLIC",
            "PRIORITY:3",
            "LOCATION:Mainstage",
            "TRANSP:OPAQUE",
            "UID:1752F7C0-2864-4EC5-A044-347454A6716B",
            "DTSTAMP:20051025T231727Z",
            "SEQUENCE:0",
            "LAST-MODIFIED:20051025T231349Z",
            "CREATED:20051025T221603Z",
            "DTSTART:20051028T210000Z",
            "SUMMARY:Thaddeus Hogarth",
            "DTEND:20051028T230000Z",
            "CATEGORIES:Appointment",
            'DESCRIPTION:Take a healthy dose of Sly and The Family Stone',
            "END:VEVENT",
            "END:VCALENDAR",
        ])
        name = 'event.ics'
        self.setRoles(['Manager']) # XXX Default Plone workflow does
                                   # not allow a 'Member' to publish,
                                   # so Calendaring fails to set the
                                   # event state if you are not
                                   # Manager.
        response = self.publish(self.folder_path + '/' + name,
                                request_method='PUT',
                                stdin=StringIO(event),
                                basic=self.basic_auth)

        self.assertEqual(response.getStatus(), 201)
        self.failUnless(name in self.folder.objectIds())
        obj = self.folder._getOb(name)
        self.assertEqual(obj.portal_type, 'Folder')

        # Folder title comes from 'X-WR-CALNAME'
        self.assertEqual(obj.Title(), 'Music')

        # The event is created inside the folder.
        obj = obj.objectValues()[0]
        self.assertEqual(obj.portal_type, 'Event')
        self.assertEqual(obj.Title(), 'Thaddeus Hogarth')
        self.assertEqual(obj.Description(),
                         'Take a healthy dose of Sly and The Family Stone')
        self.assertEqual(obj.getLocation(), 'Mainstage')
        self.assertEqual(obj.start(), DateTime('2005/10/28 19:00:00 GMT-2'))
        self.assertEqual(obj.end(), DateTime('2005/10/28 21:00:00 GMT-2'))
        # XXX Broken!
        # self.assertEqual(obj.Subject(), ('Appointment',))

        response = self.publish(self.folder_path + '/' + name +
                                '/' + obj.getId() + '/manage_DAVget',
                                request_method='GET',
                                basic=self.basic_auth)
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.failUnless('BEGIN:VCALENDAR' in body, body)
        # XXX Broken!
        # self.failUnless('Appointment' in body, body)
        self.failUnless('Mainstage' in body, body)

def test_suite():
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestDAVProperties))
    # DISABLED the metadata test, this is not yet implemented in ATCT
    ##suite.addTest(makeSuite(TestDAVMetadata))
    suite.addTest(makeSuite(TestPUTDefaultPage))
    suite.addTest(makeSuite(TestPUTDefaultMarshaller))
    suite.addTest(makeSuite(TestPUTObjects))
    suite.addTest(makeSuite(TestDAVOperations))
    suite.addTest(makeSuite(TestContentTypeRegistry))
    return suite
