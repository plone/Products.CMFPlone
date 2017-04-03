# -*- coding: utf-8 -*-
from plone.app.layout.globals.tests.base import GlobalsTestCase
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.portlets.interfaces import IPortletType
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import ILinkSchema
from zope.component import getUtility

import zope.interface


class TestLayoutView(GlobalsTestCase):
    """Tests the global layout view."""

    def afterSetUp(self):
        self.view = self.portal.restrictedTraverse('@@plone_layout')

    def testHavePortlets(self):
        have_portlets = self.view.have_portlets
        self.assertEqual(False, have_portlets('plone.leftcolumn'))
        # We have no portlet on the right in Plone 5.0
        self.assertEqual(False, have_portlets('plone.rightcolumn'))

    def testEnableColumns(self):
        # Make sure we can force a column to appear even if there are no
        # portlets
        self.app.REQUEST.set('disable_plone.leftcolumn', 0)
        self.assertEqual(True, self.view.have_portlets('plone.leftcolumn'))

    def testDisableColumns(self):
        self.setRoles(('Manager', ))

        # Now add some portlets to be sure we have columns.  For
        # simplicity we want a portlet that has no add form.  Note
        # that apparently the Calender had no add form until Plone
        # 4.3, but since 4.4 it does, so it is not fit to use here.
        portlet = getUtility(IPortletType, name='portlets.Login')
        mapping_left = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        mapping_right = self.portal.restrictedTraverse(
            '++contextportlets++plone.rightcolumn')
        for m in mapping_left.keys():
            del mapping_left[m]
        addview_left = mapping_left.restrictedTraverse('+/' + portlet.addview)

        for m in mapping_right.keys():
            del mapping_right[m]
        addview_right = mapping_right.restrictedTraverse(
            '+/' + portlet.addview)

        # This is a NullAddForm - calling it does the work
        addview_left()
        addview_right()

        # Logout, otherwise the login portlet will never show.
        self.logout()

        # Check that we do not explicitly disable the columns.  This
        # may happen if we change the request in this method or if the
        # addviews return an add-form after all.
        self.assertTrue('disable_plone.leftcolumn' not in self.app.REQUEST)
        self.assertTrue('disable_plone.rightcolumn' not in self.app.REQUEST)

        self.assertEqual(True, self.view.have_portlets('plone.leftcolumn'))
        self.app.REQUEST.set('disable_plone.leftcolumn', 1)
        self.assertEqual(False, self.view.have_portlets('plone.leftcolumn'))

        self.assertEqual(True, self.view.have_portlets('plone.rightcolumn'))
        self.app.REQUEST.set('disable_plone.rightcolumn', 1)
        self.assertEqual(False, self.view.have_portlets('plone.rightcolumn'))

    def testBodyClass(self):
        context = self.portal['front-page']
        template = context.document_view
        view = context.restrictedTraverse('@@plone_layout')
        body_class = view.bodyClass(template, view)
        assert 'section-front-page' in body_class

    def testBodyClassTemplate(self):
        context = self.portal['front-page']

        template = context.document_view
        view = context.restrictedTraverse('@@plone_layout')

        body_class = view.bodyClass(template, view)
        assert 'template-document_view' in body_class

        body_class = view.bodyClass(template, None)
        assert 'template-document_view' in body_class

        body_class = view.bodyClass(None, view)
        assert 'template-plone_layout' in body_class

    def testBodyClassWithNavigationRoot(self):
        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        context = self.folder
        view = context.restrictedTraverse('@@plone_layout')
        template = context.folder_listing
        body_class = view.bodyClass(template, view)
        assert 'section-%s' % context.getId() in body_class
        assert 'site-Members' in body_class

    def testBodyClassWithEverySection(self):
        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        self.folder.invokeFactory('Folder', 'folder2')
        self.folder.folder2.invokeFactory('Folder', 'folder3')
        self.folder.folder2.folder3.invokeFactory('Document', 'page')
        context = self.folder.folder2.folder3.page
        view = context.restrictedTraverse('@@plone_layout')
        template = context.document_view
        body_class = view.bodyClass(template, view)
        assert 'subsection-folder2 subsection-folder2-folder3' in body_class
        assert ' subsection-folder2-folder3-page' in body_class

    def testBodyClassWithEverySectionTurnedOff(self):
        registry = getUtility(IRegistry)
        registry['plone.app.layout.globals.bodyClass.depth'] = 0
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        self.folder.invokeFactory('Folder', 'folder2')
        self.folder.folder2.invokeFactory('Folder', 'folder3')
        self.folder.folder2.folder3.invokeFactory('Document', 'page')
        context = self.folder.folder2.folder3.page
        view = context.restrictedTraverse('@@plone_layout')
        template = context.document_view
        body_class = view.bodyClass(template, view)
        assert 'subsection-folder2 subsection-folder2-folder3' \
            not in body_class
        assert ' subsection-folder2-folder3-page' not in body_class

    def testBodyClassWithMarkSpecialLinksOnOff(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ILinkSchema,
            prefix="plone",
            check=False
        )

        context = self.portal['front-page']
        template = context.document_view
        view = context.restrictedTraverse('@@plone_layout')

        # Case 1
        settings.mark_special_links = False
        settings.external_links_open_new_window = False
        body_class = view.bodyClass(template, view)
        self.assertTrue('pat-markspeciallinks' not in body_class)

        # Case 2
        settings.mark_special_links = True
        settings.external_links_open_new_window = False
        body_class = view.bodyClass(template, view)
        self.assertTrue('pat-markspeciallinks' in body_class)

        # Case 3
        settings.mark_special_links = False
        settings.external_links_open_new_window = True
        body_class = view.bodyClass(template, view)
        self.assertTrue('pat-markspeciallinks' in body_class)

        # Case 4
        settings.mark_special_links = True
        settings.external_links_open_new_window = True
        body_class = view.bodyClass(template, view)
        self.assertTrue('pat-markspeciallinks' in body_class)
