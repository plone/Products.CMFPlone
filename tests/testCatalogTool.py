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

    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCatalogTool))
        return suite

