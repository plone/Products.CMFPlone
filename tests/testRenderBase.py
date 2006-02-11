#
# Tests for renderBase.py
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()


class TestRenderBase(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.folder.invokeFactory('Document', id='doc')
        self.portal.manage_addDTMLMethod('a_view', file='<dtml-var renderBase>')

    def testRenderBase(self):
        self.assertEqual(self.folder.renderBase(),
                         self.folder.absolute_url()+'/')

    def testFolderBase(self):
        base = self.publish(self.folder_path+'/renderBase')
        self.assertEqual(base.getBody(),
                         self.folder.absolute_url()+'/')

    def testFolderViewBase(self):
        base = self.publish(self.folder_path+'/a_view')
        self.assertEqual(base.getBody(),
                         self.folder.absolute_url()+'/')

    def testDocumentBase(self):
        base = self.publish(self.folder_path+'/doc/renderBase')
        self.assertEqual(base.getBody(),
                         self.folder.doc.absolute_url())

    def testDocumentViewBase(self):
        base = self.publish(self.folder_path+'/doc/a_view')
        self.assertEqual(base.getBody(),
                         self.folder.doc.absolute_url())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRenderBase))
    return suite

if __name__ == '__main__':
    framework()
