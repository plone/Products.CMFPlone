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

    def testFolderUrls(self):
        settings = PatternsSettings(self.folder, self.app.REQUEST)
        result = settings()
        self.assertEquals(result['data-base-url'], self.folder.absolute_url())
        self.assertEquals(result['data-portal-url'], self.portal.absolute_url())
        self.assertEquals(result['data-view-url'], self.folder.absolute_url())

    def testFileUrls(self):
        self.folder.invokeFactory('File', 'file1')
        file_obj = self.folder['file1']
        settings = PatternsSettings(file_obj, self.app.REQUEST)
        result = settings()
        self.assertEquals(result['data-base-url'], file_obj.absolute_url())
        self.assertEquals(
            result['data-portal-url'],
            self.portal.absolute_url()
        )
        self.assertEquals(
            result['data-view-url'],
            file_obj.absolute_url() + '/view'
        )

    def testPatternOptions(self):
        registry = getUtility(IRegistry)
        registry['plone.patternoptions'] = {
            'foo': u'{"foo": "bar"}'
        }

        settings = PatternsSettings(self.folder, self.app.REQUEST)
        result = settings()
        self.assertEquals(result['data-pat-foo'], u'{"foo": "bar"}')
