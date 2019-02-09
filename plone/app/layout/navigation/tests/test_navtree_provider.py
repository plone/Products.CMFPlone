# -*- coding: utf-8 -*-
from plone.app.layout.testing import INTEGRATION_TESTING
from plone.app.layout.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.app.testing import setRoles

import unittest


class TestNavTreeContentProvider(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        self.folder = self.portal['Members'][TEST_USER_ID]
        self.portal.Members.reindexObject()
        self.folder.reindexObject()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _get_navtree(self):
        adapter = getMultiAdapter(
            (
                self.portal, self.request.clone(),
                self.portal.restrictedTraverse('@@view')
            ),
            name='plone.navtree',
        )
        return adapter.navtree

    def test_default_settings(self):
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )

    def test_do_not_generate_tabs(self):
        self.registry['plone.generate_tabs'] = False
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html'],
        )

    def test_generate_tabs_non_folderish(self):
        self.registry['plone.nonfolderish_tabs'] = False
        self.portal.invokeFactory(
            'Document',
            'test-doc',
            title=u'A simple document (àèìòù)',
        )
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )

    def test_generate_tabs_sorted(self):
        self.portal.invokeFactory(
            'Document',
            'test-doc-2',
            title=u'Document 2',
        )
        self.portal.invokeFactory(
            'Document',
            'test-doc-1',
            title=u'Document 1',
        )
        navtree = self._get_navtree()
        # default sorting by position in parent
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/Members',
                '/plone/test-doc-2',
                '/plone/test-doc-1',
            ],
        )

        # check we can sort by title
        self.registry['plone.sort_tabs_on'] = u'sortable_title'
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/Members',
                '/plone/test-doc-1',
                '/plone/test-doc-2',
            ],
        )

        # check we can reverse sorting
        self.registry['plone.sort_tabs_reversed'] = True
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/test-doc-2',
                '/plone/test-doc-1',
                '/plone/Members',
            ],
        )

    def test_generate_tabs_displayed_types(self):
        self.registry['plone.displayed_types'] = (
            u'Image',
            u'File',
            u'Link',
            u'News Item',
            u'Document',
            u'Event',
        )
        navtree = self._get_navtree()
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
            ],
        )

    def test_generate_tabs_filter_on_state(self):
        self.registry['plone.filter_on_workflow'] = True
        navtree = self._get_navtree()
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
            ],
        )
        self.registry['plone.workflow_states_to_show'] = (u'private', )
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )

        # Let's check this works also with deep navigation
        self.registry['plone.navigation_depth'] = 2
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone/Members']],
            ['/plone/Members/test_user_1_'],
        )

    def test_generate_tabs_exclude_from_nav(self):
        self.portal.invokeFactory(
            'Folder',
            'test-folder',
            title=u'Test folder',
        )
        self.portal.invokeFactory(
            'Folder',
            'excluded-folder',
            title=u'Excluded folder',
            exclude_from_nav=True,
        )
        self.portal['excluded-folder'].invokeFactory(
            'Folder',
            'sub-folder',
            title=u'Sub folder',
        )

        navtree = self._get_navtree()
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/Members',
                '/plone/test-folder',
                '/plone/excluded-folder',
            ],
        )

        # Check also that we we have proper nesting
        self.registry['plone.navigation_depth'] = 2
        navtree = self._get_navtree()
        self.assertListEqual(
            sorted(navtree),
            ['/plone', '/plone/Members', '/plone/excluded-folder'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone/excluded-folder']],
            ['/plone/excluded-folder/sub-folder'],
        )

        self.registry['plone.navigation_depth'] = 1
        self.registry['plone.show_excluded_items'] = False
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members', '/plone/test-folder'],
        )

        # If we increase the navigation depth to 2 the sub folder in the
        # exclude folder it is there but unlinked
        self.registry['plone.navigation_depth'] = 2
        navtree = self._get_navtree()
        self.assertListEqual(
            sorted(navtree),
            ['/plone', '/plone/Members', '/plone/excluded-folder'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members', '/plone/test-folder'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone/excluded-folder']],
            ['/plone/excluded-folder/sub-folder'],
        )

        self.portal['excluded-folder']['sub-folder'].exclude_from_nav = True
        self.portal['excluded-folder']['sub-folder'].reindexObject()
        navtree = self._get_navtree()
        self.assertListEqual(
            sorted(navtree),
            ['/plone', '/plone/Members'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members', '/plone/test-folder'],
        )
