#
# Runs the ZChecker on all skins in this instance
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('ZChecker')

# Create a Plone site in the test (demo-) storage
app = ZopeTestCase.app()
PloneTestCase.setupPloneSite(app, id='portal')
ZopeTestCase.close(app)


class TestSkins(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        factory = self.portal.manage_addProduct['ZChecker']
        factory.manage_addZChecker('zchecker')

    def testSkins(self):
        '''Runs the ZChecker on skins'''
        dirs = self.portal.portal_skins.objectValues()
        for dir in dirs:
            self.portal.zchecker.checkObjects(dir.objectValues())
            

if __name__ == '__main__':
    framework(verbosity=0)

