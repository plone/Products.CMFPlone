#
# Tests the content type scripts
#

from AccessControl import Unauthorized
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

AddPortalTopics = 'Add portal topics'
import transaction
from OFS.CopySupport import CopyError

#    NOTE
#    document, link, and newsitem edit's are now validated
#    so we must pass in fields that the validators need


class TestContentTypeScripts(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(perms + [AddPortalTopics], 'Member')
        self.discussion = self.portal.portal_discussion
        self.request = self.app.REQUEST

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def testDiscussionReply(self):
        from zope.component import createObject, queryUtility
        from plone.registry.interfaces import IRegistry
        from plone.app.discussion.interfaces import IDiscussionSettings
        from plone.app.discussion.interfaces import IConversation
        self.folder.invokeFactory('Document', id='doc', title="Document")
        # Enable discussion         
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True
        # Create the conversation object
        conversation = IConversation(self.folder.doc)
        # Add a comment 
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation.addComment(comment)
        # Test the comment
        self.assertEquals(len(list(conversation.getComments())), 1)
        reply = conversation.getComments().next()
        self.assertEqual(reply.Title(), u'Anonymous on Document')
        self.assertEquals(reply.text, 'Comment text')

    def testDocumentCreate(self):
        self.folder.invokeFactory('Document', id='doc', text='data')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.folder.doc.Format(), 'text/plain')

    def testDocumentEdit(self):
        self.folder.invokeFactory('Document', id='doc')
        self.folder.doc.document_edit('html', 'data', title='Foo')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.folder.doc.Format(), 'text/html')
        self.assertEqual(self.folder.doc.Title(), 'Foo')

    def testEventCreate(self):
        self.folder.invokeFactory('Event', id='event',
                                  title = 'Foo',
                                  start_date='2003-09-18',
                                  end_date='2003-09-19')
        self.assertEqual(self.folder.event.Title(), 'Foo')
        self.failUnless(self.folder.event.start().ISO8601().startswith('2003-09-18T00:00:00'))
        self.failUnless(self.folder.event.end().ISO8601().startswith('2003-09-19T00:00:00'))

    def testEventEdit(self):
        self.folder.invokeFactory('Event', id='event')
        self.folder.event.event_edit(title='Foo',
                                     start_date='2003-09-18',
                                     end_date='2003-09-19')
        self.assertEqual(self.folder.event.Title(), 'Foo')
        self.failUnless(self.folder.event.start().ISO8601().startswith('2003-09-18T00:00:00'))
        self.failUnless(self.folder.event.end().ISO8601().startswith('2003-09-19T00:00:00'))

    def testFileCreate(self):
        self.folder.invokeFactory('File', id='file', file=dummy.File())
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testFileEdit(self):
        self.folder.invokeFactory('File', id='file')
        self.folder.file.file_edit(file=dummy.File())
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageCreate(self):
        self.folder.invokeFactory('Image', id='image', file=dummy.Image())
        self.assertEqual(str(self.folder.image.data), dummy.GIF)

    def testImageEdit(self):
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.image_edit(file=dummy.Image())
        self.assertEqual(str(self.folder.image.data), dummy.GIF)

    def testFolderCreate(self):
        self.folder.invokeFactory('Folder', id='folder', title='Foo', description='Bar')
        self.assertEqual(self.folder.folder.Title(), 'Foo')
        self.assertEqual(self.folder.folder.Description(), 'Bar')

    def testLinkCreate(self):
        self.folder.invokeFactory('Link', id='link', remote_url='http://foo.com', title='Foo')
        self.assertEqual(self.folder.link.Title(), 'Foo')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'http://foo.com')

    def testLinkEdit(self):
        self.folder.invokeFactory('Link', id='link')
        self.folder.link.link_edit('http://foo.com', title='Foo')
        self.assertEqual(self.folder.link.Title(), 'Foo')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'http://foo.com')

    def testNewsItemCreate(self):
        self.folder.invokeFactory('News Item', id='newsitem', text='data', title='Foo')
        self.assertEqual(self.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.folder.newsitem.Title(), 'Foo')

    def testNewsItemEdit(self):
        self.folder.invokeFactory('News Item', id='newsitem')
        self.folder.newsitem.newsitem_edit('data', 'plain', title='Foo')
        self.assertEqual(self.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.folder.newsitem.Title(), 'Foo')

    # Bug tests

    def testClearImageTitle(self):
        # Test for http://dev.plone.org/plone/ticket/3303
        # Should be able to clear Image title
        self.folder.invokeFactory('Image', id='image', title='Foo', file=dummy.Image())
        self.assertEqual(self.folder.image.Title(), 'Foo')
        self.folder.image.image_edit(title='')
        self.assertEqual(self.folder.image.Title(), '')

    def test_listMetaTypes(self):
        self.folder.invokeFactory('Document', id='doc')
        tool = self.portal.plone_utils
        doc = self.folder.doc
        doc.setTitle('title')
        metatypes = tool.listMetaTags(doc)
        # TODO: atm it checks only of the script can be called w/o an error

    def testObjectDeleteFailsOnGET(self):
        self.assertRaises(Unauthorized, self.folder.object_delete,)

    def testObjectDelete(self):
        self.folder.invokeFactory('Document', id='doc')
        self.setupAuthenticator()
        self.setRequestMethod('POST')
        self.folder.doc.object_delete()
        self.failIf('doc' in self.folder)


class TestEditShortName(PloneTestCase.PloneTestCase):
    # Test fix for http://dev.plone.org/plone/ticket/2246
    # Short name should be editable without specifying a file.

    def afterSetUp(self):
        self.folder.invokeFactory('File', id='file', file=dummy.File())
        self.folder.invokeFactory('Image', id='image', file=dummy.Image())

    def testFileEditNone(self):
        self.assertEqual(str(self.folder.file), dummy.TEXT)
        self.folder.file.file_edit(file=None, title='Foo')
        self.assertEqual(self.folder.file.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageEditNone(self):
        self.assertEqual(str(self.folder.image.data), dummy.GIF)
        self.folder.image.image_edit(file=None, title='Foo')
        self.assertEqual(self.folder.image.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.image.data), dummy.GIF)

    def testFileEditEmptyString(self):
        self.assertEqual(str(self.folder.file), dummy.TEXT)
        self.folder.file.file_edit(file='', title='Foo')
        self.assertEqual(self.folder.file.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.file), dummy.TEXT)

    def testImageEditEmptyString(self):
        self.assertEqual(str(self.folder.image.data), dummy.GIF)
        self.folder.image.image_edit(file='', title='Foo')
        self.assertEqual(self.folder.image.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.folder.image.data), dummy.GIF)

    def testFileEditString(self):
        self.folder.file.file_edit(file='foo')
        self.assertEqual(str(self.folder.file.getFile()), 'foo')

    def testImageEditString(self):
        self.folder.image.image_edit(file=dummy.GIF)
        self.assertEqual(str(self.folder.image.data), dummy.GIF)

    def testFileEditShortName(self):
        transaction.savepoint(optimistic=True) # make rename work
        self.folder.file.file_edit(id='fred')
        self.failUnless('fred' in self.folder)

    def testImageEditShortName(self):
        transaction.savepoint(optimistic=True) # make rename work
        self.folder.image.image_edit(id='fred')
        self.failUnless('fred' in self.folder)


class TestEditFileKeepsMimeType(PloneTestCase.PloneTestCase):
    # Tests covering http://dev.plone.org/plone/ticket/2792
    # Editing a file should not change MIME type

    def afterSetUp(self):
        self.folder.invokeFactory('File', id='file')
        self.folder.file.file_edit(file=dummy.File('foo.pdf'))
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.image_edit(file=dummy.Image('foo.gif'))

    def testFileMimeType(self):
        self.assertEqual(self.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.folder.file.getFile().content_type, 'application/pdf')

    def testImageMimeType(self):
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.content_type, 'image/gif')

    def testFileEditKeepsMimeType(self):
        self.assertEqual(self.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.folder.file.getFile().content_type, 'application/pdf')
        self.folder.file.file_edit(title='Foo')
        self.assertEqual(self.folder.file.Title(), 'Foo')
        self.assertEqual(self.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.folder.file.getFile().content_type, 'application/pdf')

    def testImageEditKeepsMimeType(self):
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.content_type, 'image/gif')
        self.folder.image.image_edit(title='Foo')
        self.assertEqual(self.folder.image.Title(), 'Foo')
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.content_type, 'image/gif')

    def testFileRenameKeepsMimeType(self):
        self.assertEqual(self.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.folder.file.getFile().content_type, 'application/pdf')
        transaction.savepoint(optimistic=True) # make rename work
        self.folder.file.file_edit(id='foo')
        self.assertEqual(self.folder.foo.Format(), 'application/pdf')
        self.assertEqual(self.folder.foo.getFile().content_type, 'application/pdf')

    def testImageRenameKeepsMimeType(self):
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.content_type, 'image/gif')
        transaction.savepoint(optimistic=True) # make rename work
        self.folder.image.image_edit(id='foo')
        self.assertEqual(self.folder.foo.Format(), 'image/gif')
        self.assertEqual(self.folder.foo.content_type, 'image/gif')


class TestFileURL(PloneTestCase.PloneTestCase):
    # Tests covering http://dev.plone.org/plone/ticket/3296
    # file:// URLs should contain correct number of slashes
    # NOTABUG: This is how urlparse.urlparse() works.

    def testFileURLWithHost(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file://foo.com/baz.txt')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file://foo.com/baz.txt')

    def testFileURLNoHost(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file:///foo.txt')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file:///foo.txt')

    def testFileURLFourSlash(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file:////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file://foo.com/baz.txt')

    def testFileURLFiveSlash(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file://///foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file:///foo.com/baz.txt')

    def testFileURLSixSlash(self):
        self.folder.invokeFactory('Link', id='link', remote_url='file://////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.folder.link.getRemoteUrl(), 'file:////foo.com/baz.txt')


class TestFileExtensions(PloneTestCase.PloneTestCase):

    file_id = 'File.2001-01-01.12345'
    image_id = 'Image.2001-01-01.12345'

    def afterSetUp(self):
        self.folder.invokeFactory('File', id=self.file_id)
        self.folder.invokeFactory('Image', id=self.image_id)
        transaction.savepoint(optimistic=True) # make rename work

    def testUploadFile(self):
        self.folder[self.file_id].file_edit(file=dummy.File('fred.txt'))
        self.failUnless('fred.txt' in self.folder)

    def testUploadImage(self):
        self.folder[self.image_id].image_edit(file=dummy.Image('fred.gif'))
        self.failUnless('fred.gif' in self.folder)

    def DISABLED_testFileRenameKeepsExtension(self):
        # XXX Wishful thinking
        self.folder[self.file_id].file_edit(id='barney')
        self.failUnless('barney.txt' in self.folder)

    def DISABLED_testImageRenameKeepsExtension(self):
        # XXX Wishful thinking
        self.folder[self.image_id].image_edit(id='barney')
        self.failUnless('barney.gif' in self.folder)


class TestBadFileIds(PloneTestCase.PloneTestCase):

    file_id = 'File.2001-01-01.12345'
    image_id = 'Image.2001-01-01.12345'

    def afterSetUp(self):
        self.folder.invokeFactory('File', id=self.file_id)
        self.folder.invokeFactory('Image', id=self.image_id)
        transaction.savepoint(optimistic=True) # make rename work

    def testUploadBadFile(self):
        # http://dev.plone.org/plone/ticket/3416
        try:
            self.folder[self.file_id].file_edit(file=dummy.File('fred%.txt'))
        except CopyError:
            # Somehow we'd get one of these *sometimes* (not consistently)
            # when running tests... since all we're testing is that the
            # object doesn't get renamed, this shouldn't matter
            pass
        self.failIf('fred%.txt' in self.folder)

    def testUploadBadImage(self):
        # http://dev.plone.org/plone/ticket/3518
        try:
            self.folder[self.image_id].image_edit(file=dummy.File('fred%.gif'))
        except CopyError:
            # (ditto - see above)
            pass
        self.failIf('fred%.gif' in self.folder)

    # TODO: Dang! No easy way to get at the validator state...


class TestImageProps(PloneTestCase.PloneTestCase):

    def testImageComputedProps(self):
        from OFS.Image import Image
        tag = Image.tag.im_func
        kw = {'_title':'some title',
              '_alt':'alt tag',
              'height':100,
              'width':100}
        # Wrap object so that ComputedAttribute gets executed.
        self.ob = dummy.ImageComputedProps(**kw).__of__(self.folder)

        endswith = ('alt="alt tag" title="some title" '
                    'height="100" width="100" />')
        self.assertEqual(tag(self.ob)[-len(endswith):], endswith)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentTypeScripts))
    suite.addTest(makeSuite(TestEditShortName))
    suite.addTest(makeSuite(TestEditFileKeepsMimeType))
    suite.addTest(makeSuite(TestFileURL))
    suite.addTest(makeSuite(TestFileExtensions))
    suite.addTest(makeSuite(TestBadFileIds))
    suite.addTest(makeSuite(TestImageProps))
    return suite
