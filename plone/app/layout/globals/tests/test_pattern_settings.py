from plone.app.layout.globals.tests.base import GlobalsTestCase
from plone.app.layout.globals.patterns_settings import PatternsSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestPatternSettings(GlobalsTestCase):
    """Ensure that the basic redirector setup is successful.
    """

    def testShouldReturnCorrectType(self):
        settings = PatternsSettings(self.folder, self.app.REQUEST)
        result = settings()
        self.assertEquals(type(result), dict)
        for key, value in result.items():
            self.assertTrue(isinstance(key, basestring))
            self.assertTrue(isinstance(value, basestring))

    def testUrls(self):
        settings = PatternsSettings(self.folder, self.app.REQUEST)
        result = settings()
        self.assertEquals(result['data-base-url'], self.folder.absolute_url())
        self.assertEquals(result['data-portal-url'], self.portal.absolute_url())

    def testPatternOptions(self):
        registry = getUtility(IRegistry)
        registry['plone.patternoptions'] = {
            'foo': u'{"foo": "bar"}'
        }

        settings = PatternsSettings(self.folder, self.app.REQUEST)
        result = settings()
        self.assertEquals(result['data-pat-foo'], u'{"foo": "bar"}')