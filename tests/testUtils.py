#
# utils tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()

from Products.CMFPlone import utils

class TestUtils(PloneTestCase.PloneTestCase):

    def testVersionTupleAlgorithm(self):
        version_map = {'1.2.3': (1, 2, 3, 'final', 0),
                       '2.1-candidate3': (2, 1, 0, 'candidate', 3),
                       '3-beta': (3, 0, 0, 'beta', 0),
                       '2.1-final1 (SVN)': (2, 1, 0, 'final', 1),
                       'foo': None,
                       '2.0a3': (2, 0, 0, 'alpha', 3),
                       '1.2 final': (1, 2, 0, 'final', 0)}
        # TODO note that '2.0a3' will currently return (2, 0, 0, 'final', 0),
        #     when really it should return None.  my regex foo is tapped. (ra)
        for v_str, v_tpl in version_map.items():
            self.failUnless(v_tpl == utils.versionTupleFromString(v_str))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtils))
    return suite

if __name__ == '__main__':
    framework()
