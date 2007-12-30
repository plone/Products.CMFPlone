from zope.app.component.hooks import setSite, setHooks
from zope.component import getSiteManager
from zope.component import queryUtility
from zope.interface import Interface

from xml.dom.minidom import parseString

from Products.GenericSetup.testing import DummySetupEnviron

from plone.portlets.interfaces import IPortletType

from plone.app.portlets.exportimport.portlets import PortletsXMLAdapter
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard
from plone.app.portlets.tests.base import PortletsTestCase

class TestImportPortlets(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        sm = getSiteManager(self.portal)
        self.importer = PortletsXMLAdapter(sm, DummySetupEnviron())
    
    def test_removePortlet(self):
        self.failUnless(queryUtility(IPortletType,
          name='portlets.Calendar') is not None)
        self.assertEqual(True,
          self.importer._removePortlet('portlets.Calendar'))
        self.failUnless(queryUtility(IPortletType,
          name='portlets.Calendar') is None)
        self.assertEqual(False, self.importer._removePortlet('foo'))
    
    def test_checkBasicPortletNodeErrors(self):
        node = parseString(_XML_INVALID_EXTEND_AND_PURGE).documentElement
        self.assertEqual(
          True, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          ) 
        node = parseString(_XML_INVALID_EXTEND_NONEXISTS).documentElement
        self.assertEqual(
          True, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          )
        node = parseString(_XML_INVALID_ADD_EXISTING).documentElement
        self.assertEqual(
          True, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          )
        node = parseString(_XML_EXTEND_EXISTING).documentElement
        self.assertEqual(
          False, self.importer._checkBasicPortletNodeErrors(node,
          ['portlets.Exists'])
          )        
    
    def test_modifyForList(self):
        node = parseString(_XML_COLUMN2).documentElement
        self.assertEqual(['foo.IColumn1'],
          self.importer._modifyForList(node, ['foo.IColumn2']))
        node = parseString(_XML_BBB_INTERFACE).documentElement
        self.assertEqual(['plone.app.portlets.interfaces.IColumn'],
          self.importer._modifyForList(node, []))
    
    def test_BBB_for(self):
        self.assertEqual([Interface], self.importer._BBB_for(None))
        self.assertEqual([], self.importer._BBB_for([]))
        self.assertEqual([Interface], self.importer._BBB_for(Interface))
        self.assertEqual([Interface], self.importer._BBB_for([Interface]))
    
    def test_initPortletNode_basic(self):
        node = parseString(_XML_BASIC).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual('Foo', portlet.title)
        self.assertEqual('Bar', portlet.description)
        self.assertEqual([IColumn], portlet.for_)
    
    def test_initPortletNode_multipleInterfaces(self):
        node = parseString(_XML_MULTIPLE_INTERFACES).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual([IColumn, IDashboard], portlet.for_)
    
    def test_initPortletNode_defaultManagerInterface(self):
        node = parseString(_XML_DEFAULT_INTERFACE).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual([Interface], portlet.for_)
    
    def test_initPortletNode_BBBInterface(self):
        node = parseString(_XML_BBB_INTERFACE).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.BBB")
        self.failUnless(portlet is not None)
        self.assertEqual([IColumn], portlet.for_)
    
    def test_initPortletNode_extend(self):
        node = parseString(_EXTENDME_SETUP).documentElement
        self.importer._initPortletNode(node)
        node = parseString(_EXTENDME_EXTENSION).documentElement
        self.importer._initPortletNode(node) 
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual([IDashboard], portlet.for_)
    
    def test_initPortletNode_purge(self):
        node = parseString(_PURGME_SETUP).documentElement
        self.importer._initPortletNode(node)
        node = parseString(_PURGEME_PURGE).documentElement
        self.importer._initPortletNode(node)
        portlet = queryUtility(IPortletType, name="portlets.New")
        self.failUnless(portlet is not None)
        self.assertEqual([IColumn], portlet.for_)
        self.assertEqual('Bar', portlet.title)
        self.assertEqual('Bar', portlet.description)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestImportPortlets))
    return suite

_XML_INVALID_EXTEND_AND_PURGE = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" extend="" purge="" />
"""

_XML_INVALID_EXTEND_NONEXISTS = """<?xml version="1.0"?>
<portlet addview="portlets.NonExists" extend="" />
"""

_XML_INVALID_ADD_EXISTING = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" title="Foo" description="Foo" />
"""

_XML_EXTEND_EXISTING = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" extend="" />
"""

_XML_COLUMN2 = """<?xml version="1.0"?>
<portlet addview="portlets.Exists" extend="">
  <for interface="foo.IColumn1" />
  <for interface="foo.IColumn2" remove="" />
</portlet>
"""

_XML_BASIC = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Bar">
  <for interface="plone.app.portlets.interfaces.IColumn" />
</portlet>

_XML_MULTIPLE_INTERFACES6 = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IColumn" />
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""

_XML_DEFAULT_INTERFACE = """<?xml version="1.0"?>
<portlet addview="portlets.New" title="Foo" description="Foo" />
"""

_XML_EXTENDME_SETUP = """<?xml version="1.0"?>
<portlet addview="portlets.ExtendMe" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IColumn" />
</portlet>
"""

_XML_EXTENDME_EXTENSION = """<?xml version="1.0"?>
<portlet addview="portlets.ExtendMe" extend="">
  <for interface="plone.app.portlets.interfaces.IColumn" remove="" />
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""

_XML_PURGEME_SETUP = """<?xml version="1.0"?>
<portlet addview="portlets.PurgeMe" title="Foo" description="Foo">
  <for interface="plone.app.portlets.interfaces.IDashboard" />
</portlet>
"""

_XML_PURGEME_PURGE = """<?xml version="1.0"?>
<portlet addview="portlets.PurgeMe" purge="" title="Bar" description="Bar">
  <for interface="plone.app.portlets.interfaces.IColumn" />
</portlet>
"""

_XML_BBB_INTERFACE = """<?xml version="1.0"?>
<portlet addview="portlets.BBB" title="Foo" description="Foo" for="plone.app.por
tlets.interfaces.IColumn" />
"""
