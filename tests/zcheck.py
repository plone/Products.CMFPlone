#
# To run the ZChecker on all skins in this instance type
#
#   $ python zcheck.py
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('ZChecker')

_print = ZopeTestCase._print

ignoredObjectIds = ['rssBody', 'RSS', 'rss_template', 'search_rss',
                    # There's no DTD for the pdf topic stuff
                    'atct_topic_pdf', 'atct_topic_pdf_template']


class TestSkins(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        factory = self.portal.manage_addProduct['ZChecker']
        factory.manage_addZChecker('zchecker')
        self.portal.zchecker.setIgnoreObjectIds(ignoredObjectIds)

    def testSkins(self):
        '''Runs the ZChecker on skins'''
        dirs = self.portal.portal_skins.objectValues()
        for dir in dirs:
            results = self.portal.zchecker.checkObjects(dir.objectValues())
            for result in results:
                self._report(result)
        _print('\n')

    def _report(self, result):
        msg = result['msg']
        obj = result['obj']
        if msg:
            _print('\n------\n%s\n' %self._skinpath(obj))
            for line in msg:
                _print('%s\n' %line)
        else:
            _print('.')

    def _skinpath(self, obj):
        path = obj.absolute_url(1)
        path = path.split('/')
        return '/'.join(path[1:])


if __name__ == '__main__':
    framework(verbosity=0)
