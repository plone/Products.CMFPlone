from datetime import datetime
from plone.app.textfield import RichTextValue
from plone.namedfile.file import NamedFile
from plone.namedfile.file import NamedImage
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests import PloneTestCase


AddPortalTopics = "Add portal topics"


class TestContentTypeScripts(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        perms = self.getPermissionsOfRole("Member")
        self.setPermissions(perms + [AddPortalTopics], "Member")
        self.request = self.app.REQUEST

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p["name"] for p in perms if p["selected"]]

    def testDocumentCreate(self):
        self.folder.invokeFactory("Document", id="doc", text=RichTextValue("data"))
        self.assertEqual(self.folder.doc.text.raw, "data")
        self.assertEqual(self.folder.doc.Format(), "text/html")

    def testEventCreate(self):
        self.folder.invokeFactory(
            "Event",
            id="event",
            title="Foo",
            start=datetime(year=2003, month=9, day=18),
            end=datetime(year=2003, month=9, day=19),
        )
        self.assertEqual(self.folder.event.Title(), "Foo")
        self.assertTrue(
            self.folder.event.start.isoformat().startswith("2003-09-18T00:00:00")
        )
        self.assertTrue(
            self.folder.event.end.isoformat().startswith("2003-09-19T00:00:00")
        )

    def testFileCreate(self):
        self.folder.invokeFactory("File", id="file", file=NamedFile(dummy.File()))
        self.assertEqual(self.folder.file.file.data, dummy.TEXT)

    def testImageCreate(self):
        self.folder.invokeFactory("Image", id="image", image=NamedImage(dummy.Image()))
        self.assertEqual(self.folder.image.image.data, dummy.GIF)

    def testFolderCreate(self):
        self.folder.invokeFactory("Folder", id="folder", title="Foo", description="Bar")
        self.assertEqual(self.folder.folder.Title(), "Foo")
        self.assertEqual(self.folder.folder.Description(), "Bar")

    def testLinkCreate(self):
        self.folder.invokeFactory(
            "Link", id="link", remoteUrl="http://foo.com", title="Foo"
        )
        self.assertEqual(self.folder.link.Title(), "Foo")
        self.assertEqual(self.folder.link.remoteUrl, "http://foo.com")

    def testNewsItemCreate(self):
        self.folder.invokeFactory(
            "News Item", id="newsitem", text=RichTextValue("data"), title="Foo"
        )
        self.assertEqual(self.folder.newsitem.text.raw, "data")
        self.assertEqual(self.folder.newsitem.Title(), "Foo")

    # Bug tests

    def test_listMetaTypes(self):
        self.folder.invokeFactory("Document", id="doc")
        tool = self.portal.plone_utils
        doc = self.folder.doc
        doc.setTitle("title")
        tool.listMetaTags(doc)
        # TODO: atm it checks only of the script can be called w/o an error


class TestFileURL(PloneTestCase.PloneTestCase):
    # Tests covering http://dev.plone.org/plone/ticket/3296
    # file:// URLs should contain correct number of slashes
    # NOTABUG: This is how urlparse.urlparse() works.

    def testFileURLWithHost(self):
        self.folder.invokeFactory("Link", id="link", remoteUrl="file://foo.com/baz.txt")
        self.assertEqual(self.folder.link.remoteUrl, "file://foo.com/baz.txt")

    def testFileURLNoHost(self):
        self.folder.invokeFactory("Link", id="link", remoteUrl="file:///foo.txt")
        self.assertEqual(self.folder.link.remoteUrl, "file:///foo.txt")

    # DX does not pass url through urlparse/urlunparse like setRemoteUrl does.
    # def testFileURLFourSlash(self):
    #     self.folder.invokeFactory('Link', id='link',
    #                               remoteUrl='file:////foo.com/baz.txt')
    #     # See urlparse.urlparse()
    #     self.assertEqual(self.folder.link.remoteUrl,
    #                      'file://foo.com/baz.txt')

    # def testFileURLFiveSlash(self):
    #     self.folder.invokeFactory('Link', id='link',
    #                               remoteUrl='file://///foo.com/baz.txt')
    #     # See urlparse.urlparse()
    #     self.assertEqual(self.folder.link.remoteUrl,
    #                      'file:///foo.com/baz.txt')

    # def testFileURLSixSlash(self):
    #     self.folder.invokeFactory('Link', id='link',
    #                               remoteUrl='file://////foo.com/baz.txt')
    #     # See urlparse.urlparse()
    #     self.assertEqual(self.folder.link.remoteUrl,
    #                      'file:////foo.com/baz.txt')


class TestImageProps(PloneTestCase.PloneTestCase):
    def testImageComputedProps(self):
        from OFS.Image import Image

        tag = Image.tag
        kw = {"_title": "some title", "_alt": "alt tag", "height": 100, "width": 100}
        # Wrap object so that ComputedAttribute gets executed.
        self.ob = dummy.ImageComputedProps(**kw).__of__(self.folder)

        endswith = 'alt="alt tag" title="some title" ' 'height="100" width="100" />'
        self.assertEqual(tag(self.ob)[-len(endswith) :], endswith)
