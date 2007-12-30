from StringIO import StringIO

from xml.dom.minidom import parseString

from zope.app.component.hooks import setSite, setHooks
from zope.component import getSiteManager
from zope.component import getUtility

from Products.GenericSetup.testing import DummySetupEnviron

from plone.portlets.interfaces import IPortletType

from plone.app.portlets.exportimport.portlets import PortletsXMLAdapter
from plone.app.portlets.tests.base import PortletsTestCase

class TestExportPortlets(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        sm = getSiteManager(self.portal)
        self.importer = self.exporter = \
          PortletsXMLAdapter(sm, DummySetupEnviron())
    
    def test_extractPortletNode(self):
        node = parseString(_XML_MULTIPLE_INTERFACES).documentElement
        self.importer._initPortletNode(node)
        portlet = getUtility(IPortletType, 'portlets.New')
        node = self.exporter._extractPortletNode('portlets.New', portlet)
        file = StringIO()
        node.writexml(file)
        file.seek(0)
        self.assertEqual("""<portlet title="Foo" addview="portlets.New" description="Foo"><for interface="plone.app.portlets.interfaces.IColumn"/><for interface="plone.app.portlets.interfaces.IDashboard"/></portlet>""", file.read())
    
    def test_extractPortletNode_defaultManagerInterface(self):
        node = parseString(_XML_EXPLICIT_DEFAULT_INTERFACE).documentElement
        self.importer._initPortletNode(Node)
        portlet = getUtility(IPortletType, 'portlets.New')
        node = self.exporter._extractPortletNode('portlets.New', portlet)
        file = StringIO()
        node.writexml(file)
        file.seek(0)
        self.assertEqual("""<portlet title="Foo" addview="portlets.New" descript
ion="Foo"/>""", file.read())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestExportPortlets))
    return suite

_XML_MULTIPLE_INTERFACES = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IColumn" />
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""

_XML_DEFAULT_INTERFACE = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo">
  <for interface="zope.interface.Interface" />
</portlet>
"""
