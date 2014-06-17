from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

AddPortalTopics = 'Add portal topics'


class TestContentTypeScripts(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(perms + [AddPortalTopics], 'Member')
        self.request = self.app.REQUEST

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def testDocumentCreate(self):
        self.folder.invokeFactory('Document', id='doc', text='data')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.folder.doc.Format(), 'text/plain')

    def testEventCreate(self):
        self.folder.invokeFactory('Event', id='event',
                                  title='Foo',
                                  start_date='2003-09-18',
                                  end_date='2003-09-19')
        self.assertEqual(self.folder.event.Title(), 'Foo')
        self.assertTrue(self.folder.event.start().ISO8601()
                            .startswith('2003-09-18T00:00:00'))
        self.assertTrue(self.folder.event.end().ISO8601()
                            .startswith('2003-09-19T00:00:00'))

    def testFileCreate(self):
        self.folder.invokeFactory('File', id='file', file=dummy.File())
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageCreate(self):
        self.folder.invokeFactory('Image', id='image', file=dummy.Image())
        self.assertEqual(str(self.folder.image.data), dummy.GIF)

    def testFolderCreate(self):
        self.folder.invokeFactory('Folder', id='folder', title='Foo',
                                  description='Bar')
        self.assertEqual(self.folder.folder.Title(), 'Foo')
        self.assertEqual(self.folder.folder.Description(), 'Bar')

    def testLinkCreate(self):
        self.folder.invokeFactory('Link', id='link',
                                  remote_url='http://foo.com', title='Foo')
        self.assertEqual(self.folder.link.Title(), 'Foo')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'http://foo.com')

    def testNewsItemCreate(self):
        self.folder.invokeFactory('News Item', id='newsitem',
                                  text='data', title='Foo')
        self.assertEqual(self.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.folder.newsitem.Title(), 'Foo')

    # Bug tests

    def test_listMetaTypes(self):
        self.folder.invokeFactory('Document', id='doc')
        tool = self.portal.plone_utils
        doc = self.folder.doc
        doc.setTitle('title')
        tool.listMetaTags(doc)
        # TODO: atm it checks only of the script can be called w/o an error


class TestFileURL(PloneTestCase.PloneTestCase):
    # Tests covering http://dev.plone.org/plone/ticket/3296
    # file:// URLs should contain correct number of slashes
    # NOTABUG: This is how urlparse.urlparse() works.

    def testFileURLWithHost(self):
        self.folder.invokeFactory('Link', id='link',
                                  remote_url='file://foo.com/baz.txt')
        self.assertEqual(self.folder.link.getRemoteUrl(),
                         'file://foo.com/baz.txt')

    def testFileURLNoHost(self):
        self.folder.invokeFactory('Link', id='link',
                                  remote_url='file:///foo.txt')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file:///foo.txt')

    def testFileURLFourSlash(self):
        self.folder.invokeFactory('Link', id='link',
                                  remote_url='file:////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(),
                         'file://foo.com/baz.txt')

    def testFileURLFiveSlash(self):
        self.folder.invokeFactory('Link', id='link',
                                  remote_url='file://///foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(),
                         'file:///foo.com/baz.txt')

    def testFileURLSixSlash(self):
        self.folder.invokeFactory('Link', id='link',
                                  remote_url='file://////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(),
                         'file:////foo.com/baz.txt')


class TestImageProps(PloneTestCase.PloneTestCase):

    def testImageComputedProps(self):
        from OFS.Image import Image
        tag = Image.tag.im_func
        kw = {'_title': 'some title',
              '_alt': 'alt tag',
              'height': 100,
              'width': 100}
        # Wrap object so that ComputedAttribute gets executed.
        self.ob = dummy.ImageComputedProps(**kw).__of__(self.folder)

        endswith = ('alt="alt tag" title="some title" '
                    'height="100" width="100" />')
        self.assertEqual(tag(self.ob)[-len(endswith):], endswith)
