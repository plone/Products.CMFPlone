# This test confirms that views assigned to theme-specific layers (a la
# plone.theme) take precedence over views assigned to layers from other
# add-on products (a la plone.browserlayer).

from Products.CMFPlone.tests import PloneTestCase
from zope.publisher.browser import TestRequest

from zope.event import notify
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.interfaces import BeforeTraverseEvent
from plone.browserlayer.utils import register_layer, unregister_layer
from plonetheme.sunburst.browser.interfaces import IThemeSpecific


class IAdditiveLayer(Interface):
    pass


class TestBrowserLayerPrecedence(PloneTestCase.FunctionalTestCase):

    def _get_request_interfaces(self):
        request = TestRequest()
        notify(BeforeTraverseEvent(self.portal, request))
        iro = list(request.__provides__.__iro__)
        return iro

    def testCustomBrowserLayerHasPrecedenceOverDefaultLayer(self):
        register_layer(IAdditiveLayer, 'Plone.testlayer')
        iro = self._get_request_interfaces()
        unregister_layer('Plone.testlayer')

        self.assertTrue(iro.index(IAdditiveLayer) < iro.index(IDefaultBrowserLayer))

    def testThemeSpecificLayerTakesHighestPrecedence(self):
        register_layer(IAdditiveLayer, 'Plone.testlayer')
        iro = self._get_request_interfaces()
        unregister_layer('Plone.testlayer')

        self.assertTrue(iro.index(IThemeSpecific) < iro.index(IAdditiveLayer),
            'Theme-specific browser layers should take precedence over other '
            'browser layers.')
