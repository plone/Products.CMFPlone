import unittest
from urllib2 import HTTPError
from plone.testing.z2 import Browser

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING


class TestBadAcquisition(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def test_not_found_when_acquired_content(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        self.assertTrue('a_folder' in self.portal.objectIds())
        import transaction
        transaction.commit()
        browser = Browser(self.app)
        browser.open(self.portal.a_page.absolute_url())
        error = None
        try:
            url = self.portal.absolute_url() + '/a_folder/a_page'
            browser.open(url)
        except HTTPError, e:
            error = e
        self.assertTrue(
            error is not None,
            msg='Acquired content should not be published.')
        self.assertEqual(404, error.code)
