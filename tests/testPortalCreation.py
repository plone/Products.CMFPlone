#
# Tests portal creation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base


class TestPortalCreation(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # The portal has already been set up, so there 
        # is little to do. :-|
        self.membership = self.portal.portal_membership

    def testPloneSkins(self):
        # Plone skins should have been set up
        self.failUnless(hasattr(self.folder, 'plone_powered.gif'))

    def testDefaultView(self):
        # index_html should render
        self.portal.index_html()

    def testMembersIndexHtml(self):
        # index_html for Members folder should be a Page Template
        members = self.membership.getMembersFolder()
        self.assertEqual(aq_base(members).meta_type, 'Large Plone Folder')
        self.failUnless(hasattr(aq_base(members), 'index_html'))
        # getitem works
        self.assertEqual(aq_base(members)['index_html'].meta_type, 'Page Template')
        self.assertEqual(members['index_html'].meta_type, 'Page Template')
        # _getOb works
        self.assertEqual(aq_base(members)._getOb('index_html').meta_type, 'Page Template')
        self.assertEqual(members._getOb('index_html').meta_type, 'Page Template')
        # getattr works when called explicitly
        self.assertEqual(aq_base(members).__getattr__('index_html').meta_type, 'Page Template')
        self.assertEqual(members.__getattr__('index_html').meta_type, 'Page Template')

    def testLargePloneFolderFuckup(self):
        members = self.membership.getMembersFolder()
        self.assertEqual(aq_base(members).meta_type, 'Large Plone Folder')
        # This works now as hazmat fixed LargePloneFolder, hurray.
        self.assertEqual(members.index_html.meta_type, 'Page Template')

            
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPortalCreation))
        return suite

