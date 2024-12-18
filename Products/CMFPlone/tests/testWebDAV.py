from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import bbb
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests import PloneTestCase

import io


html = """\
<html>
<head><title>Foo</title></head>
<body>Bar</body>
</html>
"""


class TestDAVProperties(PloneTestCase.PloneTestCase):
    def testPropertiesToolTitle(self):
        ptool = getToolByName(self.portal, "portal_properties")
        psets = dict(ptool.propertysheets.items())
        self.assertTrue("webdav" in psets.keys())
        default = psets["webdav"]
        items = dict(default.propertyItems())
        self.assertTrue("displayname" in items.keys())
        self.assertEqual(items["displayname"], ptool.title)


class TestPUTObjects(PloneTestCase.PloneTestCase):
    # PUT objects into Plone including special cases like index_html.
    # Confirms fix for http://dev.plone.org/plone/ticket/1375

    def afterSetUp(self):
        self.basic_auth = f"{TEST_USER_NAME}:{TEST_USER_PASSWORD}"
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def testPUTDocument(self):
        # Create a new document via FTP/DAV
        response = self.publish(
            self.folder_path + "/new_html",
            env={"CONTENT_TYPE": "text/html"},
            request_method="PUT",
            stdin=io.StringIO(html),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("new_html" in self.folder)
        self.assertEqual(self.folder.new_html.portal_type, "Document")
        self.assertEqual(self.folder.new_html.text.raw, html)

    def testPUTTextDocumentRSTNoContentType(self):
        # Create a new document via FTP/DAV, some clients do not send
        # a proper Content-Type header.
        response = self.publish(
            self.folder_path + "/test.rst",
            env={"CONTENT_LENGTH": "0"},
            request_method="PUT",
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.rst" in self.folder)
        self.assertEqual(self.folder["test.rst"].portal_type, "Document")
        self.assertIsNone(self.folder["test.rst"].text)

    def testPUTTextDocumentTXTNoContentType(self):
        # Create a new document via FTP/DAV, some clients do not send
        # a proper Content-Type header.
        response = self.publish(
            self.folder_path + "/test.txt",
            env={"CONTENT_LENGTH": "0"},
            request_method="PUT",
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.txt" in self.folder)
        self.assertEqual(self.folder["test.txt"].portal_type, "Document")
        self.assertIsNone(self.folder["test.txt"].text)

    def testPUTTextDocumentININoContentType(self):
        # Create a new document via FTP/DAV, some clients do not send
        # a proper Content-Type header.
        response = self.publish(
            self.folder_path + "/test.ini",
            env={"CONTENT_LENGTH": "0"},
            request_method="PUT",
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.ini" in self.folder)
        self.assertEqual(self.folder["test.ini"].portal_type, "Document")
        self.assertIsNone(self.folder["test.ini"].text)

    def testPUTIndexHtmlDocument(self):
        # Create an index_html document via FTP/DAV
        response = self.publish(
            self.folder_path + "/index_html",
            env={"CONTENT_TYPE": "text/html"},
            request_method="PUT",
            stdin=io.StringIO(html),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("index_html" in self.folder)
        self.assertEqual(self.folder.index_html.portal_type, "Document")
        self.assertEqual(self.folder.index_html.text.raw, html)
        self.assertEqual(self.folder._getOb("index_html").text.raw, html)

    def testPUTImage(self):
        # Create a new image via FTP/DAV
        response = self.publish(
            self.folder_path + "/new_image",
            env={"CONTENT_TYPE": "image/gif"},
            request_method="PUT",
            stdin=io.StringIO(dummy.GIF),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("new_image" in self.folder)
        self.assertEqual(self.folder.new_image.portal_type, "Image")
        self.assertEqual(str(self.folder.new_image.image.data), dummy.GIF)

    def testPUTImageGIFNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(
            self.folder_path + "/test.gif",
            env={"CONTENT_LENGTH": len(dummy.GIF)},
            request_method="PUT",
            stdin=io.StringIO(dummy.GIF),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.gif" in self.folder)
        self.assertEqual(self.folder["test.gif"].portal_type, "Image")
        self.assertEqual(str(self.folder["test.gif"].image.data), dummy.GIF)

    def testPUTImageJPGNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(
            self.folder_path + "/test.jpg",
            env={"CONTENT_LENGTH": len(dummy.GIF)},
            request_method="PUT",
            stdin=io.StringIO(dummy.GIF),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.jpg" in self.folder)
        self.assertEqual(self.folder["test.jpg"].portal_type, "Image")
        self.assertEqual(str(self.folder["test.jpg"].image.data), dummy.GIF)

    def testPUTImagePNGNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(
            self.folder_path + "/test.png",
            env={"CONTENT_LENGTH": len(dummy.GIF)},
            request_method="PUT",
            stdin=io.StringIO(dummy.GIF),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.png" in self.folder)
        self.assertEqual(self.folder["test.png"].portal_type, "Image")
        self.assertEqual(str(self.folder["test.png"].image.data), dummy.GIF)

    def testPUTImageTIFFNoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(
            self.folder_path + "/test.tiff",
            env={"CONTENT_LENGTH": len(dummy.GIF)},
            request_method="PUT",
            stdin=io.StringIO(dummy.GIF),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.tiff" in self.folder)
        self.assertEqual(self.folder["test.tiff"].portal_type, "Image")
        self.assertEqual(str(self.folder["test.tiff"].image.data), dummy.GIF)

    def testPUTImageICONoContentType(self):
        # Create a new image via FTP/DAV, some clients do not send a
        # proper Content-Type header.  Note we are uploading a GIF
        # image, but the content_type_registry only looks at the
        # extension. We just send a GIF image so that PIL doesn't
        # complain.
        response = self.publish(
            self.folder_path + "/test.ico",
            env={"CONTENT_LENGTH": len(dummy.GIF)},
            request_method="PUT",
            stdin=io.StringIO(dummy.GIF),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("test.ico" in self.folder)
        self.assertEqual(
            self.folder["test.ico"].portal_type,
            "Image",
            "If you are on a Mac and this fails, please see: "
            "http://plone.org/documentation/error/unittest to fix.",
        )
        self.assertEqual(str(self.folder["test.ico"].image.data), dummy.GIF)

    def testPUTIndexHtmlImage(self):
        # Create a new image named index_html via FTP/DAV
        response = self.publish(
            self.folder_path + "/index_html",
            env={"CONTENT_TYPE": "image/gif"},
            request_method="PUT",
            stdin=io.StringIO(dummy.GIF),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("index_html" in self.folder)
        self.assertEqual(self.folder.index_html.portal_type, "Image")
        self.assertEqual(str(self.folder.index_html.image.data), dummy.GIF)

    def testPUTDocumentIntoPortal(self):
        # Create a new document in the portal via FTP/DAV
        self.setRoles(["Manager"])

        response = self.publish(
            self.portal_path + "/new_html",
            env={"CONTENT_TYPE": "text/html"},
            request_method="PUT",
            stdin=io.StringIO(html),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("new_html" in self.portal)
        self.assertEqual(self.portal.new_html.portal_type, "Document")
        self.assertEqual(self.portal.new_html.text.raw, html)

    def testPUTIndexHtmlDocumentIntoPortal(self):
        # Create an index_html document in the portal via FTP/DAV
        self.setRoles(["Manager"])

        response = self.publish(
            self.portal_path + "/index_html",
            env={"CONTENT_TYPE": "text/html"},
            request_method="PUT",
            stdin=io.StringIO(html),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("index_html" in self.portal)
        self.assertEqual(self.portal.index_html.portal_type, "Document")
        self.assertEqual(self.portal.index_html.text.raw, html)
        self.assertEqual(self.portal._getOb("index_html").text.raw, html)


class TestPUTIndexHtml(PloneTestCase.PloneTestCase):
    """Move the webdav_index_html_put.txt doctest to here.

    There used to be a problem when creating an object named 'index_html'
    in Plone using WebDAV.

    The problem occurred because Plone Folder's 'index_html' was a
    ComputedAttribute used to acquire index_html from skins when there was
    no index_html Document on the portal root.

    However, this ComputedAttribute didn't handle WebDAV 'PUT' request
    correctly. This test ensures that the fix doesn't regress.

    It could be duplicate with the tests above.
    """

    def afterSetUp(self):
        self.basic_auth = f"{TEST_USER_NAME}:{TEST_USER_PASSWORD}"
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)
        self.body = "I am the walrus"
        self.length = len(self.body)

    def testPUTIndexHtml(self):
        # Create an index_html document via FTP/DAV
        self.assertFalse("index_html" in self.folder)

        response = self.publish(
            self.folder_path + "/index_html",
            basic=self.basic_auth,
            env={"Content-Length": self.length},
            stdin=io.StringIO(self.body),
            request_method="PUT",
            handle_errors=False,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("index_html" in self.folder)
        self.assertEqual(self.folder.index_html.meta_type, "Dexterity Item")

    def testPUTIndexHtmlIntoPortal(self):
        # Create an index_html document in the portal via FTP/DAV
        self.assertFalse("index_html" in self.portal)
        self.setRoles(["Manager"])

        response = self.publish(
            self.portal_path + "/index_html",
            basic=self.basic_auth,
            env={"Content-Length": self.length},
            stdin=io.StringIO(self.body),
            request_method="PUT",
            handle_errors=False,
        )

        self.assertEqual(response.getStatus(), 201)
        self.assertTrue("index_html" in self.portal)
        self.assertEqual(self.portal.index_html.meta_type, "Dexterity Item")


class TestDAVOperations(PloneTestCase.FunctionalTestCase):
    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.basic_auth = f"{SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        self.portal_path = self.portal.absolute_url(1)
        self.folder_path = self.folder.absolute_url(1)

    def test_document_propfind_index_html_exist_folder(self):
        self.folder.invokeFactory("Folder", "sub")
        self.folder.sub.invokeFactory("Document", "index_html")
        self.assertTrue("index_html" in self.folder.sub)

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(
            self.folder_path + "/sub/index_html",
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_document_propfind_index_html_non_exist_folder(self):
        self.folder.invokeFactory("Folder", "sub")
        self.assertFalse("index_html" in self.folder.sub)

        # Do a PROPFIND on folder/index_html, this needs to result in a
        # NotFound.
        response = self.publish(
            self.folder_path + "/sub/index_html",
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_document_propfind_index_html_exist_portal(self):
        if "index_html" not in self.portal:
            self.portal.invokeFactory("Document", "index_html")

        self.assertTrue("index_html" in self.portal)

        # Do a PROPFIND on folder/index_html, this needs to result in a 207
        response = self.publish(
            self.portal_path + "/index_html",
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_document_propfind_index_html_non_exist_portal(self):
        if "index_html" in self.portal:
            self.portal.manage_delObjects("index_html")

        self.assertFalse("index_html" in self.portal)

        # Do a PROPFIND on portal/index_html, this needs to result in a
        # NotFound.
        response = self.publish(
            self.portal_path + "/index_html",
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 404, response.getBody())

    def test_propfind_portal_root_index_html_exists(self):
        if "index_html" not in self.portal:
            self.portal.invokeFactory("Document", "index_html")

        self.assertTrue("index_html" in self.portal)

        # Do a PROPFIND on portal, this needs to result in a 207
        response = self.publish(
            self.portal_path,
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_portal_root_index_html_not_exists(self):
        if "index_html" in self.portal:
            self.portal.manage_delObjects("index_html")

        self.assertFalse("index_html" in self.portal)

        # Do a PROPFIND on portal, this needs to result in a 207
        response = self.publish(
            self.portal_path,
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_folder_index_html_exists(self):
        if "index_html" not in self.folder:
            self.folder.invokeFactory("Document", "index_html")

        self.assertTrue("index_html" in self.folder)

        # Do a PROPFIND on folder, this needs to result in a 207
        response = self.publish(
            self.folder_path,
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 207, response.getBody())

    def test_propfind_folder_index_html_not_exists(self):
        if "index_html" in self.folder:
            self.folder.manage_delObjects("index_html")

        self.assertFalse("index_html" in self.folder)

        # Do a PROPFIND on folder, this needs to result in a 207
        response = self.publish(
            self.folder_path,
            request_method="PROPFIND",
            env={"HTTP_DEPTH": "0"},
            stdin=io.StringIO(),
            basic=self.basic_auth,
        )

        self.assertEqual(response.getStatus(), 207, response.getBody())


def test_suite():
    import unittest

    if bbb.HAS_ZSERVER:
        return unittest.TestSuite((
            unittest.defaultTestLoader.loadTestsFromTestCase(TestDAVProperties),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestPUTObjects),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestPUTIndexHtml),
            unittest.defaultTestLoader.loadTestsFromTestCase(TestDAVOperations),
        ))

    # return empty suite
    return unittest.TestSuite()
