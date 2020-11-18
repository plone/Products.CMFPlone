# -*- coding: utf-8 -*-
# This test confirms that views assigned to theme-specific layers (a la
# plone.theme) take precedence over views assigned to layers from other
# add-on products (a la plone.browserlayer).

from plone.app.testing import PloneSandboxLayer
from plone.app.testing.bbb import PloneTestCase
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from plone.browserlayer.utils import register_layer, unregister_layer
from Products.CMFPlone.interfaces import IDefaultPloneLayer
from zope.component import getGlobalSiteManager
from zope.event import notify
from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides
from zope.interface import Interface
from zope.publisher.browser import setDefaultSkin
from zope.publisher.interfaces.browser import IBrowserSkinType
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.interfaces import BeforeTraverseEvent

import unittest


class PloneThemeLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import Products.CMFPlone.tests
        self.loadZCML(
            'test_browserlayer.zcml',
            package=Products.CMFPlone.tests,
        )


PLONETHEME_FIXTURE = PloneThemeLayer()

PLONETHEME_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONETHEME_FIXTURE,),
    name="PloneTheme:Functional")

PLONETHEME_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONETHEME_FIXTURE,),
    name="PloneTheme:Integration")


class IThemeSpecific(IDefaultPloneLayer):
    pass


class IMyTheme(IDefaultPloneLayer):
    """Marker interface used in the tests
    """


class IAdditiveLayer(Interface):
    pass


class TestBrowserLayerPrecedence(PloneTestCase):

    def _get_request_interfaces(self):
        request = self.layer['request']
        # Reset _plonebrowerlayer_ marker, so that we can still register
        # additional layers for testing. (WTF here?)
        del request._plonebrowserlayer_
        notify(BeforeTraverseEvent(self.portal, request))
        iro = list(request.__provides__.__iro__)
        return iro

    def testCustomBrowserLayerHasPrecedenceOverDefaultLayer(self):
        register_layer(IAdditiveLayer, 'Plone.testlayer')
        iro = self._get_request_interfaces()
        unregister_layer('Plone.testlayer')

        self.assertTrue(iro.index(IAdditiveLayer) <
                        iro.index(IDefaultBrowserLayer))


class IAdditiveLayerExtendingDefault(IDefaultPloneLayer):
    pass


class LayerPrecedenceTestCase(unittest.TestCase):
    """This test confirms that views assigned to theme-specific layers
       take precedence over views assigned to other kinds of layers.
    """

    layer = PLONETHEME_INTEGRATION_TESTING

    additive_layer = None
    theme_layer = None

    def setUp(self):
        self.portal = self.layer['portal']
        gsm = getGlobalSiteManager()
        if self.theme_layer is not None:
            self._skin_name = self.portal.portal_skins.getDefaultSkin()
            self._old_theme_layer = gsm.queryUtility(IBrowserSkinType,
                                                     name=self._skin_name)
            gsm.registerUtility(self.theme_layer,
                                IBrowserSkinType,
                                self._skin_name)

    def _get_request_interfaces(self):
        request = self.layer['request']
        setDefaultSkin(request)
        orig_iro = list(directlyProvidedBy(request).__iro__)
        directlyProvides(request, [self.additive_layer] + orig_iro)
        # Reset markers so that we can still register new skins and
        # browserlayers
        del request._plonebrowserlayer_
        del request._plonetheme_
        notify(BeforeTraverseEvent(self.portal, request))
        iro = list(request.__provides__.__iro__)
        return iro

    def testLayerPrecedence(self):
        iro = self._get_request_interfaces()
        if self.theme_layer is not None:
            theme_layer_pos = iro.index(self.theme_layer)
            plone_default_pos = iro.index(IDefaultPloneLayer)
        additive_layer_pos = iro.index(self.additive_layer)
        zope_default_pos = iro.index(IDefaultBrowserLayer)

        # We want to have the theme layer first, followed by additive layers,
        # followed by default layers.
        if self.theme_layer is not None:
            self.assertEqual(theme_layer_pos, 0)
            self.assertTrue(theme_layer_pos < additive_layer_pos)
            # for BBB, IDefaultPloneLayer is not present
            # unless there are theme layers which extend them.
            self.assertTrue(additive_layer_pos < plone_default_pos)
        self.assertTrue(additive_layer_pos < zope_default_pos)

    def beforeTearDown(self):
        gsm = getGlobalSiteManager()
        if self.theme_layer is not None:
            res = gsm.unregisterUtility(provided=IBrowserSkinType,
                                        name=self._skin_name)
            self.assertTrue(res)
            if self._old_theme_layer is not None:
                gsm.registerUtility(self._old_theme_layer,
                                    IBrowserSkinType,
                                    self._skin_name)


class TestPrecedenceWithAdditiveLayerExtendingInterface(
    LayerPrecedenceTestCase
):
    theme_layer = IThemeSpecific
    additive_layer = IAdditiveLayer


class TestPrecedenceWithAdditiveLayerExtendingDefault(LayerPrecedenceTestCase):
    theme_layer = IThemeSpecific
    additive_layer = IAdditiveLayerExtendingDefault


class TestPrecedenceWithNoThemeLayer(LayerPrecedenceTestCase):
    theme_layer = None
    additive_layer = IAdditiveLayer
