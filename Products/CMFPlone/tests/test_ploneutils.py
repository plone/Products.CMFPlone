import unittest
import re

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TestPloneTool(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.plone_utils = self.portal.plone_utils

    def test_deleteObjectsByPaths(self):
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        a_page = self.portal['a_page']
        self.plone_utils.deleteObjectsByPaths([a_page.absolute_url_path()])
        self.assertFalse('a_page' in self.portal.objectIds())

    def test_deleteObjectsByPaths_relative_path_raises(self):
        self.assertRaises(
            ValueError,
            self.plone_utils.deleteObjectsByPaths,
            ['relative'],
            handle_errors=False
        )

    def test_delete_wrongly_acquired_object_through_deleteObjectsByPaths(self):
        '''
        Do not delete wrongly acquired object through folder_contents
        See https://dev.plone.org/ticket/13603

        '''
        # prepare content
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        a_folder = self.portal['a_folder']
        a_folder.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in a_folder.objectIds())
        a_page_in_folder = a_folder['a_page']
        path = a_page_in_folder.absolute_url_path()

        # first request to delete
        self.plone_utils.deleteObjectsByPaths([path])
        self.assertFalse('a_page' in a_folder.objectIds())
        self.assertTrue('a_page' in self.portal.objectIds())

        # second request to delete
        self.plone_utils.deleteObjectsByPaths([path])
        self.assertTrue(
            'a_page' in self.portal.objectIds(),
            'acquired content should not be deleted.'
        )

    def _get_authenticator(self):
        url = '/plone/login_password'
        login = self.portal.restrictedTraverse(url)
        res = login()
        m = re.search('name="_authenticator" value="([^"]*)"', res)
        if m:
            return m.group(1)
        return ''

    def test_delete_wrongly_acquired_object_through_object_delete(self):
        '''
        Do not delete wrongly acquired object through Actions Delete.
        See https://dev.plone.org/ticket/13603
        '''
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])

        # prepare content
        self.portal.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        self.portal.invokeFactory('Folder', 'a_folder')
        a_folder = self.portal['a_folder']
        a_folder.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in a_folder.objectIds())
        a_page_in_folder = a_folder['a_page']

        # prepare fake request
        physical_path = list(a_page_in_folder.getPhysicalPath())
        physical_path.append('object_delete')
        url = '/'.join(physical_path)
        request = self.layer['request']
        request.set('URL', url)
        url2 = '/'.join(physical_path[:-2])
        request.set('URL2', url2)
        request.environ['REQUEST_METHOD'] = 'POST'
        csrf_token = self._get_authenticator()
        request.form.update({
            '_authenticator': csrf_token,
        })

        # simulate call to object_delete
        object_delete = self.portal.restrictedTraverse(url)
        object_delete()
        self.assertFalse('a_page' in a_folder.objectIds())
        self.assertTrue('a_page' in self.portal.objectIds())

        # simulate second call to object_delete
        object_delete = self.portal.restrictedTraverse(url)
        object_delete()
        self.assertTrue(
            'a_page' in self.portal.objectIds(),
            'acquired content should not be deleted.'
        )
