import unittest

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING


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

    def test_deleteObjectsByPaths_wrongly_acquired_object(self):
        '''
        Do not delete wrongly acquired object.
        See https://dev.plone.org/ticket/13603
        '''
        self.portal.invokeFactory('Folder', 'a_page')
        self.assertTrue('a_page' in self.portal.objectIds())
        a_page_folder = self.portal['a_page']
        a_page_folder.invokeFactory('Document', 'a_page')
        self.assertTrue('a_page' in a_page_folder.objectIds())
        a_page = a_page_folder['a_page']
        path = a_page.absolute_url_path()
        self.plone_utils.deleteObjectsByPaths([path])
        self.assertFalse('a_page' in a_page_folder.objectIds())
        self.plone_utils.deleteObjectsByPaths([path])
        self.assertTrue('a_page' in self.portal.objectIds())
