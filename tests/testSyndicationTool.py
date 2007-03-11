#
# SyndicationTool tests
#

from AccessControl import Unauthorized
from Products.CMFPlone.tests import PloneTestCase


class TestSyndicationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.syndication = self.portal.portal_syndication
        self.folder.invokeFactory('Document','doc1')
        self.folder.invokeFactory('Document','doc2')
        self.doc1 = self.folder.doc1
        self.doc2 = self.folder.doc2
        #Enable syndication sitewide
        self.syndication.editProperties(isAllowed=True)
        #Enable syndication on folder
        self.syndication.enableSyndication(self.folder)

    def testIsSiteSyndicationAllowed(self):
        # Make sure isSiteSyndicationAllowed returns proper value so that tabs
        # appear
        self.failUnless(self.syndication.isSiteSyndicationAllowed())
        self.syndication.editProperties(isAllowed=False)
        self.failIf(self.syndication.isSiteSyndicationAllowed())

    def testIsSyndicationAllowed(self):
        # Make sure isSyndicationAllowed returns proper value so that the
        # action appears
        self.failUnless(self.syndication.isSyndicationAllowed(self.folder))
        self.syndication.disableSyndication(self.folder)
        self.failIf(self.syndication.isSyndicationAllowed(self.folder))

    def testGetSyndicatableContent(self):
        content = self.syndication.getSyndicatableContent(self.folder)
        self.assertEqual(len(content),2)

    def testOwnerCanEnableAndDisableSyndication(self):
        self.setRoles(['Owner'])
        self.syndication.disableSyndication(self.folder)
        self.failIf(self.syndication.isSyndicationAllowed(self.folder))
        self.syndication.enableSyndication(self.folder)
        self.failUnless(self.syndication.isSyndicationAllowed(self.folder))
        self.logout()
        self.assertRaises(Unauthorized, self.syndication.enableSyndication,
                          self.folder)
        self.assertRaises(Unauthorized, self.syndication.disableSyndication,
                          self.folder)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSyndicationTool))
    return suite
