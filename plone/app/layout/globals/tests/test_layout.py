from plone.portlets.interfaces import IPortletType
from zope.component import getUtility
import zope.interface

from plone.app.layout.globals.tests.base import GlobalsTestCase
from plone.app.layout.navigation.interfaces import INavigationRoot


class TestLayoutView(GlobalsTestCase):
    """Tests the global layout view."""

    def afterSetUp(self):
        self.view = self.portal.restrictedTraverse('@@plone_layout')

    def testHavePortlets(self):
        have_portlets = self.view.have_portlets
        self.assertEqual(False, have_portlets('plone.leftcolumn'))
        self.assertEqual(False, have_portlets('plone.rightcolumn'))

    def testDisableColumns(self):
        self.setRoles(('Manager', ))

        # Make sure we can force a column to appear even if there are no portlets
        self.app.REQUEST.set('disable_plone.leftcolumn', 0)
        self.assertEqual(True, self.view.have_portlets('plone.leftcolumn'))

        # Now add some portlets to be sure we have columns
        portlet = getUtility(IPortletType, name='portlets.Calendar')
        mapping_left = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        mapping_right = self.portal.restrictedTraverse('++contextportlets++plone.rightcolumn')
        for m in mapping_left.keys():
            del mapping_left[m]
        addview_left = mapping_left.restrictedTraverse('+/' + portlet.addview)

        for m in mapping_right.keys():
            del mapping_right[m]
        addview_right = mapping_right.restrictedTraverse('+/' + portlet.addview)

        # This is a NullAddForm - calling it does the work
        addview_left()
        addview_right()

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

    def testBodyClassWithNavigationRoot(self):
        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        context = self.folder
        view = context.restrictedTraverse('@@plone_layout')
        template = context.folder_listing
        body_class = view.bodyClass(template, view)
        assert 'section-%s'%context.getId() in body_class
        assert 'site-Members' in body_class


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
