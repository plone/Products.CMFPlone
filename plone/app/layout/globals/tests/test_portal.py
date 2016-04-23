# -*- coding: utf-8 -*-
from plone.app.layout.globals.tests.base import GlobalsTestCase
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRoot
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ILanguageSchema
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.interfaces import ISiteSchema
from zope.component import getUtility
from zope.event import notify
from zope.i18n.locales import locales
from zope.traversing.interfaces import BeforeTraverseEvent

import zope.interface


class TestPortalStateView(GlobalsTestCase):
    """Ensure that the basic redirector setup is successful.
    """

    def afterSetUp(self):
        self.view = self.folder.restrictedTraverse('@@plone_portal_state')

    def test_portal(self):
        self.assertEqual(self.view.portal(), self.portal)

    def test_portal_title(self):
        registry = getUtility(IRegistry)
        self.site_settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.site_settings.site_title = u'My title'
        self.assertEqual(self.view.portal_title(), 'My title')

    def test_portal_url(self):
        self.assertEqual(self.view.portal_url(), self.portal.absolute_url())

    def test_navigation_root(self):
        self.assertEqual(self.view.navigation_root(), self.portal)

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEqual(view.navigation_root(), members)

    def test_navigation_root_path(self):
        self.assertEqual(self.view.navigation_root_path(), '/plone')
        self.assertEqual(
            self.view.navigation_root_path(), getNavigationRoot(self.folder))

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEqual(
            view.navigation_root_path(),
            '/plone/Members'
        )
        self.assertEqual(
            view.navigation_root_path(), getNavigationRoot(self.folder))

    def test_navigation_root_title(self):
        self.portal.Title = "Portal title"
        self.assertEqual(self.view.navigation_root_title(), "Portal title")

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEqual(view.navigation_root_title(), members.Title())

    def test_navigation_root_url(self):
        url = self.app.REQUEST.physicalPathToURL(
            getNavigationRoot(self.folder))
        self.assertEqual(
            self.view.navigation_root_url(), 'http://nohost/plone')
        self.assertEqual(self.view.navigation_root_url(), url)

        # mark a folder "between" self.folder and self.portal with
        # INavigationRoot
        members = self.portal['Members']
        zope.interface.alsoProvides(members, INavigationRoot)
        view = members.restrictedTraverse('@@plone_portal_state')
        self.assertEqual(
            view.navigation_root_url(),
            'http://nohost/plone/Members'
        )
        url = self.app.REQUEST.physicalPathToURL(getNavigationRoot(members))
        self.assertEqual(view.navigation_root_url(), url)

    def test_default_language(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix="plone")
        settings.default_language = 'no'
        self.assertEqual(self.view.default_language(), 'no')

    def test_language(self):
        self.app.REQUEST.set('LANGUAGE', 'no')
        self.assertEqual(self.view.language(), 'no')

    def test_locale(self):
        # Set up registry so that no is an accepted language and that the
        # language information from the request is actually being used.
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        settings.use_request_negotiation = True
        settings.available_languages.append('no')

        no = locales.getLocale('no', None, None)
        self.app.REQUEST.set('HTTP_ACCEPT_LANGUAGE', 'no')

        # Push request through the BeforeTraverseEvent handler again to
        # update language settings
        notify(BeforeTraverseEvent(self.portal, self.portal.REQUEST))
        self.assertEqual(self.view.locale(), no)

    def test_is_not_rtl(self):
        self.app.REQUEST.set('LANGUAGE', 'no')
        self.assertEqual(self.view.is_rtl(), False)

    def test_is_rtl(self):
        self.app.REQUEST.set('LANGUAGE', 'he')
        self.assertEqual(self.view.is_rtl(), True)
        self.app.REQUEST.set('LANGUAGE', 'ar_DZ')
        self.assertEqual(self.view.is_rtl(), True)

    def test_member(self):
        self.assertEqual(
            self.view.member().id,
            self.portal.portal_membership.getAuthenticatedMember().id
        )

    def test_anonymous(self):
        self.assertEqual(self.view.anonymous(), False)
        self.logout()
        del self.app.REQUEST.__annotations__
        self.assertEqual(self.view.anonymous(), True)

    def test_friendly_types(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISearchSchema, prefix="plone")
        settings.types_not_searched = ('Document',)
        self.assertFalse('Document' in self.view.friendly_types())
