#
# CatalogTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base


class TestCatalogTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def testPloneLexiconIsZCTextLexicon(self):
        # Lexicon should be a ZCTextIndex lexicon
        self.failUnless(hasattr(aq_base(self.catalog), 'plone_lexicon'))
        self.assertEqual(self.catalog.plone_lexicon.meta_type, 'ZCTextIndex Lexicon')

    def testSearchableTextIsZCTextIndex(self):
        # SearchableText index should be a ZCTextIndex
        self.assertEqual(self.catalog.Indexes['SearchableText'].__class__.__name__,
                         'ZCTextIndex')

    def testManageAfterAddIfLexiconExists(self):
        # Should be able to copy/paste a portal containing 
        # a catalog tool. Triggers manage_afterAdd of portal_catalog
        # thereby exposing a bug which is now going to be fixed.
        from AccessControl.SecurityManagement import newSecurityManager
        user = self.app.acl_users.getUserById('PloneTestCase').__of__(self.app.acl_users)
        newSecurityManager(None, user)
        cb = self.app.manage_copyObjects(['portal'])
        self.app.manage_pasteObjects(cb)
        self.failUnless(hasattr(self.app, 'copy_of_portal'))

    def testSearchReturnsDocumentWhenPermissionIsTroughLocalRole(self):
        uf = self.portal.acl_users
        # I do not know yet how to proceed
        # have to ask stefan holek

    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCatalogTool))
        return suite

