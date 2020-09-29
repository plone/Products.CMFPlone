# This test confirms that views assigned to theme-specific layers (a la
# plone.theme) take precedence over views assigned to layers from other
# add-on products (a la plone.browserlayer).

from plone.app.testing.bbb import PloneTestCase

from zope.event import notify
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.interfaces import BeforeTraverseEvent
from plone.browserlayer.utils import register_layer, unregister_layer


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
