from zope.component import getMultiAdapter
from AccessControl import Unauthorized
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.interfaces.syndication import IFeedSettings


class TestSyndicationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.syndication = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name="syndication-tool")
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.invokeFactory('Document', 'doc2')
        self.doc1 = self.folder.doc1
        self.doc2 = self.folder.doc2
        #Enable syndication on folder
        settings = IFeedSettings(self.folder)
        settings.enabled = True

    def testIsSiteSyndicationAllowed(self):
        # Make sure isSiteSyndicationAllowed returns proper value so that tabs
        # appear
        self.assertTrue(self.syndication.site_enabled())
        self.syndication.editProperties(isAllowed=False)
        self.assertTrue(self.syndication.site_enabled())

    def testIsSyndicationAllowed(self):
        # Make sure isSyndicationAllowed returns proper value so that the
        # action appears
        self.assertTrue(self.syndication.isSyndicationAllowed(self.folder))
        self.syndication.disableSyndication(self.folder)
        self.assertFalse(self.syndication.isSyndicationAllowed(self.folder))

    def testGetSyndicatableContent(self):
        content = self.syndication.getSyndicatableContent(self.folder)
        self.assertEqual(len(content), 2)

    def testOwnerCanEnableAndDisableSyndication(self):
        self.setRoles(['Owner'])
        self.syndication.disableSyndication(self.folder)
        self.assertFalse(self.syndication.isSyndicationAllowed(self.folder))
        self.syndication.enableSyndication(self.folder)
        self.assertTrue(self.syndication.isSyndicationAllowed(self.folder))
        self.logout()
        self.assertRaises(Unauthorized, self.syndication.enableSyndication,
                          self.folder)
        self.assertRaises(Unauthorized, self.syndication.disableSyndication,
                          self.folder)