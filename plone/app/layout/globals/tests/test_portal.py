from plone.app.layout.globals.tests.base import GlobalsTestCase

from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRoot
from zope.i18n.locales import locales
import zope.interface


class TestPortalStateView(GlobalsTestCase):
    """Ensure that the basic redirector setup is successful.
    """

    def afterSetUp(self):
        self.view = self.folder.restrictedTraverse('@@plone_portal_state')

    def test_portal(self):
        self.assertEquals(self.view.portal(), self.portal)

    def test_portal_title(self):
        self.portal.title = 'My title'
        self.assertEquals(self.view.portal_title(), 'My title')

    def test_portal_url(self):
        self.assertEquals(self.view.portal_url(), self.portal.absolute_url())

    def test_navigation_root(self):
        self.assertEquals(self.view.navigation_root(), self.portal)

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEquals(view.navigation_root(), members)

    def test_navigation_root_path(self):
        self.assertEquals(self.view.navigation_root_path(), '/plone')
        self.assertEquals(self.view.navigation_root_path(), getNavigationRoot(self.folder))

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEquals(view.navigation_root_path(),
                         '/plone/Members')
        self.assertEquals(view.navigation_root_path(), getNavigationRoot(self.folder))

    def test_navigation_root_title(self):
        self.portal.Title = "Portal title"
        self.assertEquals(self.view.navigation_root_title(), "Portal title")

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEquals(view.navigation_root_title(), members.Title())

    def test_navigation_root_url(self):
        url = self.app.REQUEST.physicalPathToURL(getNavigationRoot(self.folder))
        self.assertEquals(self.view.navigation_root_url(), 'http://nohost/plone')
        self.assertEquals(self.view.navigation_root_url(), url)

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEquals(view.navigation_root_url(),
                          'http://nohost/plone/Members')
        url = self.app.REQUEST.physicalPathToURL(getNavigationRoot(members))
        self.assertEquals(view.navigation_root_url(), url)

    def test_default_language(self):
        self.portal.portal_properties.site_properties.default_language = 'no'
        self.assertEquals(self.view.default_language(), 'no')

    def test_language(self):
        self.app.REQUEST.set('LANGUAGE', 'no')
        self.assertEquals(self.view.language(), 'no')

    def test_locale(self):
        self.app.REQUEST.set('HTTP_ACCEPT_LANGUAGE', 'no')
        no = locales.getLocale('no', None, None)
        self.assertEquals(self.view.locale(), no)

    def test_is_not_rtl(self):
        self.app.REQUEST.set('LANGUAGE', 'no')
        self.assertEquals(self.view.is_rtl(), False)

    def test_is_rtl(self):
        self.app.REQUEST.set('LANGUAGE', 'he')
        self.assertEquals(self.view.is_rtl(), True)
        self.app.REQUEST.set('LANGUAGE', 'ar_DZ')
        self.assertEquals(self.view.is_rtl(), True)

    def test_member(self):
        self.assertEquals(self.view.member(), self.portal.portal_membership.getAuthenticatedMember())

    def test_anonymous(self):
        self.assertEquals(self.view.anonymous(), False)
        self.logout()
        del self.app.REQUEST.__annotations__
        self.assertEquals(self.view.anonymous(), True)

    def test_friendly_types(self):
        self.portal.portal_properties.site_properties.types_not_searched = ('Document', )
        self.failIf('Document' in self.view.friendly_types())


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
