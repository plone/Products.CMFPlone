"""
Test redirection support end-to-end.
"""

import unittest

import transaction

from plone.testing import z2
from plone.app import testing as pa_testing

from Products.CMFCore.utils import getToolByName

from plone.app.redirector import testing


class FunctionalRedirectTest(unittest.TestCase):
    """
    Test redirection support end-to-end.
    """

    layer = testing.PLONE_APP_REDIRECTOR_FUNCTIONAL_TESTING

    def setUp(self):
        """
        Rename a document so there's a working redirect in place.
        """
        self.portal = self.layer['portal']
        pa_testing.setRoles(self.portal, pa_testing.TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory("Folder", "folder")
        self.folder = self.portal.folder
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.doActionFor(self.folder, 'publish')
        self.folder.invokeFactory('Document', 'foo-document')
        workflow.doActionFor(self.folder['foo-document'], 'publish')
        transaction.savepoint(1)
        self.folder.manage_renameObject('foo-document', 'bar-document')
        transaction.commit()

        self.browser = z2.Browser(self.layer['app'])

    def test_redirect(self):
        """
        A simple redirect returns the correct status and headers.
        """
        self.browser.addHeader('Accept', 'text/html')
        self.browser.open(self.folder.absolute_url() + '/foo-document')
        self.assertEqual(
            self.browser.url, self.folder['bar-document'].absolute_url(),
            'Wrong redirect HTTP response location')
