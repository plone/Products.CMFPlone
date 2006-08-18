#
# Exportimport adapter tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase

from Products.CMFPlone.FactoryTool import FactoryTool
from OFS.Folder import Folder

_FACTORYTOOL_XML = """\
<?xml version="1.0"?>
<object name="portal_factory" meta_type="Plone Factory Tool">
 <factorytypes>
  <type portal_type="Folder"/>
  <type portal_type="Document"/>
 </factorytypes>
</object>
"""


class DummyTypesTool(Folder):

    id = 'portal_types'
    meta_type = 'Dummy Types Tool'

    def listContentTypes(self):
        return ('Folder', 'Document')


class PortalFactoryXMLAdapterTests(BodyAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFPlone.exportimport.factorytool \
                    import PortalFactoryXMLAdapter
        return PortalFactoryXMLAdapter

    def _populate(self, obj):
        obj.manage_setPortalFactoryTypes(listOfTypeIds=('Folder', 'Document'))

    def setUp(self):
        self.site = Folder('site')
        self.site.portal_types = DummyTypesTool()
        self.site.portal_factory = FactoryTool()

        self._obj = self.site.portal_factory
        self._BODY = _FACTORYTOOL_XML


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PortalFactoryXMLAdapterTests))
    return suite

if __name__ == '__main__':
    framework()

