# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces import ISiteSchema
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.viewlets.common import ContentViewsViewlet
from plone.app.layout.viewlets.common import LogoViewlet
from plone.app.layout.viewlets.common import TitleViewlet
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.protect import authenticator as auth
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import noLongerProvides


# Red pixel with filename pixel.png
SITE_LOGO_BASE64 = 'filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgAA'\
                   'AAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAAAA'\
                   'ElFTkSuQmCC'


class TestViewletBase(ViewletsTestCase):
    """Test the base class for the viewlets.
    """

    def test_update(self):
        request = self.app.REQUEST
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Folder', 'f1')
        context = getattr(self.portal, 'f1')
        alsoProvides(context, INavigationRoot)
        viewlet = ViewletBase(context, request, None, None)
        viewlet.update()
        self.assertEqual(viewlet.site_url, "http://nohost/plone")
        self.assertEqual(viewlet.navigation_root_url, "http://nohost/plone/f1")


class TestContentViewsViewlet(ViewletsTestCase):
    """Test the content views viewlet.
    """

    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.folder.test.unmarkCreationFlag()
        self.folder.setTitle(u"Folder")

    def _invalidateRequestMemoizations(self):
        try:
            del self.app.REQUEST.__annotations__
        except AttributeError:
            pass

    def testSet1OnPortalRoot(self):
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.portal.absolute_url()
        view = ContentViewsViewlet(self.portal, self.app.REQUEST, None)
        view.update()
        self.assertEqual(view.tabSet1[0]['id'], 'folderContents')

    def testSet1NonStructuralFolder(self):
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url()
        directlyProvides(self.folder, INonStructuralFolder)
        view = ContentViewsViewlet(self.folder, self.app.REQUEST, None)
        view.update()
        noLongerProvides(self.folder, INonStructuralFolder)
        self.assertEqual(1, len([t for t in view.tabSet1 if t[
                         'id'] == 'folderContents']))

    def testSet1(self):
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = '%s/edit?_authenticator=%s' % (
            self.folder.test.absolute_url(),
            auth.createToken()
        )
        view = ContentViewsViewlet(self.folder.test, self.app.REQUEST, None)
        view.update()
        self.assertEqual(1, len([t for t in view.tabSet1 if t[
                         'id'] == 'folderContents']))
        self.assertEqual(['edit'], [t['id'] for t in view.tabSet1 if t['selected']])

    def testTitleViewlet(self):
        """Title viewlet renders navigation root title
        """
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url()
        directlyProvides(self.folder, INavigationRoot)
        viewlet = TitleViewlet(self.folder.test, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.site_title,
                         "Test default page &mdash; Folder")

    def testTitleViewletInPortalfactory(self):
        """Title viewlet renders navigation root title in portal factory
        """
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()

        factory_folder = self.folder.portal_factory
        factory_document = (factory_folder
                            .restrictedTraverse('Document/document'))
        self.app.REQUEST['ACTUAL_URL'] = factory_document.absolute_url()

        directlyProvides(self.folder, INavigationRoot)
        viewlet = TitleViewlet(factory_document, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.site_title,
                         u'Add Page &mdash; Folder')

    def testLogoViewletDefault(self):
        """Logo links towards navigation root
        """
        self._invalidateRequestMemoizations()
        self.loginAsPortalOwner()
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url()
        directlyProvides(self.folder, INavigationRoot)
        viewlet = LogoViewlet(self.folder.test, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.navigation_root_title, "Folder")
        # there is no theme yet in Plone 5, so we see the old png logo
        self.assertTrue("logo.png" in viewlet.img_src)

    def testLogoViewletRegistry(self):
        """If logo is defined in plone.app.registry, use that one.
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        settings.site_logo = SITE_LOGO_BASE64

        viewlet = LogoViewlet(self.folder.test, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(
            'http://nohost/plone/@@site-logo/pixel.png'
            in viewlet.img_src)
