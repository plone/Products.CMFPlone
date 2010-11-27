#
# Exportimport adapter tests
#

from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase

from five.localsitemanager import make_objectmanager_site
from zope.site.hooks import setHooks, setSite
from zope.component import getSiteManager

from OFS.Folder import Folder
from Products.CMFCore.interfaces import ITypesTool

from Products.CMFPlone.FactoryTool import FactoryTool

_FACTORYTOOL_XML = """\
<?xml version="1.0"?>
<object name="portal_factory" meta_type="Plone Factory Tool">
 <factorytypes>
  <type portal_type="Document"/>
  <type portal_type="Folder"/>
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
        setHooks()
        self.site = Folder('site')
        make_objectmanager_site(self.site)
        setSite(self.site)
        sm = getSiteManager()
        self.site.portal_types = DummyTypesTool()
        sm.registerUtility(self.site.portal_types, ITypesTool)
        self.site.portal_factory = FactoryTool()

        self._obj = self.site.portal_factory
        self._BODY = _FACTORYTOOL_XML


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PortalFactoryXMLAdapterTests))
    return suite
