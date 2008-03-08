from zope.app.component.hooks import setSite, setHooks

from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.cache import render_cachekey

class MockBrain(object):
    def getPath(self):
        return u"some/path"

    modified = u"2002-01-01"

class MockLocation(object):
    def __init__(self, name):
        self.__name__ = name

class MockRenderer(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def _data(self):
        return [MockBrain(), MockBrain()]

    manager = MockLocation('some_manager')
    data = MockLocation('some_assignment')

class TestCacheKey(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testRenderCachekey(self):
        context = self.folder
        renderer = MockRenderer(context, context.REQUEST)

        key1 = render_cachekey(None, renderer) 
        renderer.manager.__name__ += '__changed__'
        key2 = render_cachekey(None, renderer)

        self.failUnless(key1 != key2)

    def testAnonymousFlag(self):
        context = self.folder
        renderer = MockRenderer(context, context.REQUEST)

        key1 = render_cachekey(None, renderer)
        self.logout()
        key2 = render_cachekey(None, renderer)

        self.assertNotEqual(key1, key2)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCacheKey))
    return suite
