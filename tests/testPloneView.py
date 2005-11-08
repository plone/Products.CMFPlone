#
# Test methods used to make ...
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.component import getView

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from Products.CMFPlone.utils import _createObjectByType

from Products.CMFPlone.URLTool import URLTool

class TestNavigationView(PloneTestCase.PloneTestCase):
    """Tests the global plone view.  """

    def testView(self):
        view =  getView(self.portal, 'plone', self.app.REQUEST)
        assert isinstance(view.utool(), URLTool)
        assert view.portal() is self.portal
        assert view.portal_object() is self.portal

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNavigationView))
    return suite

if __name__ == '__main__':
    framework()
