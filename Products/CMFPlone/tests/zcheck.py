#
# To run the ZChecker on all skins in this instance type
#
# $ ./bin/zopectl test -q --nowarn -s Products.CMFPlone --tests-pattern zcheck
#

__version__ = '0.3.0'

from Testing import ZopeTestCase
from Testing.ZopeTestCase import _print

ZopeTestCase.installProduct('PlacelessTranslationService')
ZopeTestCase.installProduct('ZChecker')

from Products.CMFPlone.tests import PloneTestCase
from Products.PloneTestCase import setup

ignoredObjectIds = ['rssBody', 'RSS', 'rss_template', 'search_rss',
                    'test_ecmascripts',
                    # There is no DTD for the pdf topic stuff
                    'atct_topic_pdf', 'atct_topic_pdf_template']

if setup.PLONE30:
    # Ignore until it is no longer DTML
    ignoredObjectIds += ['mail_password_template']


class TestSkins(PloneTestCase.PloneTestCase):
    # Note: This looks like a unit test but isn't

    def afterSetUp(self):
        factory = self.portal.manage_addProduct['ZChecker']
        factory.manage_addZChecker('zchecker')
        self.portal.zchecker.setIgnoreObjectIds(ignoredObjectIds)
        import sys
        self.verbose = not '-q' in sys.argv

    def testSkins(self):
        '''Runs the ZChecker on skins'''
        dirs = self.portal.portal_skins.objectValues()
        for dir in dirs:
            results = self.portal.zchecker.checkObjects(dir.objectValues())
            for result in results:
                self._report(result)
        if self.verbose:
            _print('\n')

    def _report(self, result):
        msg = result['msg']
        obj = result['obj']
        if msg:
            if self.verbose:
                _print('\n')
            _print('------\n%s\n' % self._skinpath(obj))
            for line in msg:
                _print('%s\n' % line)
        else:
            if self.verbose:
                _print('.')

    def _skinpath(self, obj):
        return '/'.join(obj.getPhysicalPath()[2:])

    def _filepath(self, obj):
        filepath = getattr(obj, 'getObjectFSPath', None)
        if filepath is not None:
            return filepath()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSkins))
    return suite

