#
# Tests the content type scripts
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

AddPortalTopics = 'Add portal topics'
from DateTime import DateTime
from Products.CMFPlone import LargePloneFolder


# Fake upload object
class File:
    __allow_access_to_unprotected_subobjects__ = 1
    filename = 'foo.gif'
    def seek(*args): pass
    def tell(*args): return 0
    def read(*args): return 'file_contents'


#XXX NOTE
#    document, link, and newsitem edit's are now validated
#    so we must pass in fields that the validators need
#    such as title on a favorite's link_edit

class TestContentTypeScripts(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(perms + [AddPortalTopics], 'Member')
        self.discussion = self.portal.portal_discussion
        self.request = self.app.REQUEST
        # Don't pay for catalog maintenance
        self.portal.manage_delObjects('portal_catalog')

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def testDiscussionReply(self):
        self.folder.invokeFactory('Document', id='doc')
        # Create the talkback object
        self.discussion.overrideDiscussionFor(self.folder.doc, 1)
        self.discussion.getDiscussionFor(self.folder.doc)
        # Now test it
        self.folder.doc.talkback.discussion_reply('Foo', 'blah')
        talkback = self.discussion.getDiscussionFor(self.folder.doc)
        reply = talkback.objectValues()[0]
        self.assertEqual(reply.Title(), 'Foo')
        self.assertEqual(reply.EditableBody(), 'blah')

    def testDocumentEdit(self):
        self.folder.invokeFactory('Document', id='doc')
        self.folder.doc.document_edit('plain', 'data', title='Foo')
        self.assertEqual(self.folder.doc.EditableBody(), 'data')

    def testEventEdit(self):
        self.folder.invokeFactory('Event', id='event')
        self.folder.event.event_edit(title='Foo', 
                                     start_date='2003-09-18',
                                     end_date='2003-09-19')
        self.assertEqual(self.folder.event.Title(), 'Foo')
        self.assertEqual(self.folder.event.start().ISO(), '2003-09-18 00:00:00')
        self.assertEqual(self.folder.event.end().ISO(), '2003-09-19 00:00:00')

    def testFavoriteEdit(self):
        self.folder.invokeFactory('Favorite', id='favorite')
        self.folder.favorite.link_edit('bar/baz.html', title='Foo')
        self.assertEqual(self.folder.favorite.getRemoteUrl(),
                         '%s/bar/baz.html' % self.portal.portal_url())

    def testFileEdit(self):
        self.folder.invokeFactory('File', id='file')
        self.folder.file.file_edit(file=File())
        self.assertEqual(str(self.folder.file), 'file_contents')

    def testImageEdit(self):
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.image_edit(file=File())
        self.assertEqual(str(self.folder.image.data), 'file_contents')

    def testFolderEdit(self):
        self.folder.invokeFactory('Folder', id='folder')
        self.folder.folder.folder_edit('Foo', 'Bar')
        self.assertEqual(self.folder.folder.Title(), 'Foo')
        self.assertEqual(self.folder.folder.Description(), 'Bar')

    def testLargePloneFolderEdit(self):
        LargePloneFolder.addLargePloneFolder(self.folder, id='lpf')
        self.folder.lpf.folder_edit('Foo', 'Bar')
        self.assertEqual(self.folder.lpf.Title(), 'Foo')
        self.assertEqual(self.folder.lpf.Description(), 'Bar')

    def testLinkEdit(self):
        self.folder.invokeFactory('Link', id='link')
        self.folder.link.link_edit('http://foo.com', title='Foo')
        self.assertEqual(self.folder.link.getRemoteUrl(), 'http://foo.com')

    def testNewsItemEdit(self):
        self.folder.invokeFactory('News Item', id='newsitem')
        self.folder.newsitem.newsitem_edit('data', 'plain', title='Foo')
        self.assertEqual(self.folder.newsitem.EditableBody(), 'data')

    def testTopicEditTopic(self):
        self.folder.invokeFactory('Topic', id='topic')
        self.folder.topic.topic_editTopic(1, 'topic', title='Foo')
        self.assertEqual(self.folder.topic.Title(), 'Foo')

    #def testTopicEditCriteria(self):
    #    self.folder.invokeFactory('Topic', id='topic')
    #    # TODO: Analyze that funky data structure


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestContentTypeScripts))
        return suite

