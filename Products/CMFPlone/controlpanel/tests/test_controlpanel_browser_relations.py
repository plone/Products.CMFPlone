import unittest

from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING


class RelationsControlPanelFunctionalTest(unittest.TestCase):
    """Test that links and actions in controlpanel starts with to absolute portal url."""

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def _add_broken_relation(self):
        import transaction
        from persistent.list import PersistentList
        from z3c.relationfield import RelationValue
        from zope.component import getUtility
        from zope.intid.interfaces import IIntIds
        from zope.lifecycleevent import modified

        self.portal.invokeFactory("Document", id="doc1", title="doc1")
        doc1 = self.portal["doc1"]
        self.portal.invokeFactory("Document", id="doc2", title="doc2")
        doc2 = self.portal["doc2"]

        intids = getUtility(IIntIds)
        doc1.relatedItems = PersistentList()
        doc1.relatedItems.append(RelationValue(intids.getId(doc2)))
        modified(doc1)
        self.portal._delObject("doc2")
        transaction.commit()

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )

    def test_inspect_realtions_form_action(self):
        from io import StringIO

        from lxml import etree

        self.browser.open(f"{self.portal_url}/@@inspect-relations")
        tree = etree.parse(StringIO(self.browser.contents), etree.HTMLParser())
        action_url = tree.xpath("//form[@id='relationinfo']/@action")[0]
        self.assertTrue(
            action_url.startswith(self.portal_url),
            "URL in relationinfo form should start with portal url",
        )

    def test_rebuild_relations_links(self):
        from io import StringIO

        from lxml import etree

        # first we need a broken relation
        # for conditional rendering alert panel in controlpanel
        self._add_broken_relation()

        self.browser.open(f"{self.portal_url}/@@inspect-relations")
        tree = etree.parse(StringIO(self.browser.contents), etree.HTMLParser())
        hrefs = tree.xpath(
            "//div[@id='content-core']//a[contains(@href, '@@rebuild-relations')]/@href"
        )
        for href in hrefs:
            self.assertTrue(
                href.startswith(self.portal_url),
                "URL in Link should start with portal url",
            )
