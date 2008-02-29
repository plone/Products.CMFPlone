import time
import transaction

from zope.interface import Interface
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.component.interfaces import IFactory

from zope.component import getSiteManager

from plone.app.portlets.tests.base import PortletsTestCase

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.browser import BrowserView

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.context import TarballExportContext

from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase

from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.portlets.manager import PortletManager
from plone.portlets.utils import registerPortletType

from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.interfaces import IColumn

from plone.app.portlets.browser.adding import PortletAdding
from plone.app.portlets.utils import assignment_mapping_from_key

class DummyView(BrowserView):
    pass

# A sample portlet

from zope.interface import implements
from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

class ITestPortlet(IPortletDataProvider):
    test_text = schema.TextLine(title=u"Test")
    test_bool = schema.Bool(title=u"Test")
    test_tuple = schema.Tuple(title=u"Test",
                              value_type=schema.Choice(vocabulary="plone.app.vocabularies.WorkflowStates"))

class TestAssignment(base.Assignment):
    implements(ITestPortlet)
    
    test_text = None
    test_bool = None
    test_tuple = None
    
    title = "Sample portlet"

class TestRenderer(base.Renderer):
    def render(self):
        return "Portlet for testing"

class TestAddForm(base.AddForm):
    form_fields = form.Fields(ITestPortlet)
    label = u"Test portlet"

    def create(self, data):
        a = TestAssignment()
        a.title = data.get('title', u"")
        return a

class TestEditForm(base.EditForm):
    form_fields = form.Fields(ITestPortlet)
    label = u"Test portlet"

# A test portlet manager

class ITestColumn(IColumn):
    pass

zcml_string = """\
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:browser="http://namespaces.zope.org/browser"
           xmlns:plone="http://namespaces.plone.org/plone"
           xmlns:gs="http://namespaces.zope.org/genericsetup"
           package="plone.app.portlets">

    <plone:portlet
        name="portlets.test.Test"
        interface="plone.app.portlets.tests.test_configuration.ITestPortlet"
        assignment="plone.app.portlets.tests.test_configuration.TestAssignment"
        renderer="plone.app.portlets.tests.test_configuration.TestRenderer"
        addview="plone.app.portlets.tests.test_configuration.TestAddForm"
        editview="plone.app.portlets.tests.test_configuration.TestEditForm"
        />
        
    <gs:registerProfile
        name="testing"
        title="plone.app.portlets testing"
        description="Used for testing only" 
        directory="tests/profiles/testing"
        for="Products.CMFCore.interfaces.ISiteRoot"
        provides="Products.GenericSetup.interfaces.EXTENSION"
        />
        
</configure>
"""

class TestPortletZCMLLayer(PloneSite):
    
    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        zcml.load_string(zcml_string)
        fiveconfigure.debug_mode = False

    @classmethod
    def tearDown(cls):
        pass
        
class TestPortletGSLayer(TestPortletZCMLLayer):
    
    @classmethod
    def setUp(cls):
        app = ZopeTestCase.app()
        portal = app.plone
        
        portal_setup = portal.portal_setup
        portal_setup.runAllImportStepsFromProfile('profile-plone.app.portlets:testing')
        
        transaction.commit()
        ZopeTestCase.close(app)

    @classmethod
    def tearDown(cls):
        pass

class TestZCML(PortletsTestCase):

    layer = TestPortletZCMLLayer
    
    def testPortletTypeInterfaceRegistered(self):
        iface = getUtility(IPortletTypeInterface, name=u"portlets.test.Test")
        self.assertEquals(ITestPortlet, iface)
        
    def testFactoryRegistered(self):
        factory = getUtility(IFactory, name=u"portlets.test.Test")
        self.assertEquals(TestAssignment, factory._callable)
    
    def testRendererRegistered(self):
        context = self.portal
        request = self.portal.REQUEST
        view = DummyView(context, request)
        manager = PortletManager()
        assignment = TestAssignment()
        
        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, TestRenderer))
        
    def testAddViewRegistered(self):
        request = self.portal.REQUEST
        adding = PortletAdding(self.portal, request)
        
        addview = getMultiAdapter((adding, request), name=u"portlets.test.Test")
        self.failUnless(isinstance(addview, TestAddForm))
        
    def testEditViewRegistered(self):
        assignment = TestAssignment()
        request = self.portal.REQUEST
        
        editview = getMultiAdapter((assignment, request), name=u"edit")
        self.failUnless(isinstance(editview, TestEditForm))

class TestGenericSetup(PortletsTestCase):
    
    layer = TestPortletGSLayer
    
    def testPortletManagerInstalled(self):
        manager = getUtility(IPortletManager, name=u"test.testcolumn")
        self.failUnless(ITestColumn.providedBy(manager))
    
    def testPortletTypeRegistered(self):
        portlet_type = getUtility(IPortletType, name=u"portlets.test.Test")
        self.assertEquals("Test portlet", portlet_type.title)
        self.assertEquals("A test portlet", portlet_type.description)
        self.assertEquals('portlets.test.Test', portlet_type.addview)
        self.assertEquals([Interface], portlet_type.for_)
        
    def testAssignmentCreatedAndOrdered(self):
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        self.assertEquals(3, len(mapping))
        self.assertEquals(['test.portlet3', 'test.portlet2', 'test.portlet1'], list(mapping.keys()))
        
    def testAssignmentPropertiesSet(self):
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        
        assignment = mapping['test.portlet1']
        self.assertEquals(u'Test pr\xf6p 1', assignment.test_text)
        self.assertEquals(False, assignment.test_bool)
        self.assertEquals((u'published', u'private'), assignment.test_tuple)
        
        assignment = mapping['test.portlet2']
        self.assertEquals('Test prop 2', assignment.test_text)
        self.assertEquals(True, assignment.test_bool)
        self.assertEquals((), assignment.test_tuple)
        
        assignment = mapping['test.portlet3']
        self.assertEquals(None, assignment.test_text)
        self.assertEquals(None, assignment.test_bool)
        self.assertEquals(None, assignment.test_tuple)
        
    def testAssignmentRemoval(self):
        portal_setup = self.portal.portal_setup
        portal_setup.runAllImportStepsFromProfile('profile-plone.app.portlets:testing')

        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")

        # initally there should be no portlet7
        self.assertEqual(mapping.get('test.portlet7', None), None)

        # now we add one
        portlet_factory = getUtility(IFactory, name='portlets.test.Test')
        assignment = portlet_factory()
        mapping['test.portlet7'] = assignment

        # make sure it's there
        self.assertNotEqual(mapping.get('test.portlet7', None), None)

        # wait a bit or we get duplicate ids on import
        time.sleep(1)
        # run the profile
        portal_setup.runAllImportStepsFromProfile('profile-plone.app.portlets:testing')

        # and should have got rid of it again
        self.assertEqual(mapping.get('test.portlet7', None), None)

    def testBlacklisting(self):
        news = self.portal.news
        manager = getUtility(IPortletManager, name=u"test.testcolumn")
        
        assignable = getMultiAdapter((news, manager), ILocalPortletAssignmentManager)
        self.assertEquals(True, assignable.getBlacklistStatus(CONTEXT_CATEGORY))
        self.assertEquals(False, assignable.getBlacklistStatus(GROUP_CATEGORY))
        self.assertEquals(None, assignable.getBlacklistStatus(CONTENT_TYPE_CATEGORY))

    def testPurge(self):
        sm = getSiteManager()
        context = TarballExportContext(self.portal.portal_setup)
        handler = getMultiAdapter((sm, context), IBody, name=u'plone.portlets')
        handler._purgePortlets()
        
        manager = queryUtility(IPortletManager, name=u"test.testcolumn")
        self.assertEquals(None, manager)
        
    def testExport(self):
        sm = getSiteManager()
        context = TarballExportContext(self.portal.portal_setup)
        handler = getMultiAdapter((sm, context), IBody, name=u'plone.portlets')
        handler._purgePortlets()
        
        time.sleep(1)
        
        portal_setup = self.portal.portal_setup
        portal_setup.runAllImportStepsFromProfile('profile-plone.app.portlets:testing')

        expected = """\
<?xml version="1.0"?>
<portlets>
 <portletmanager name="test.testcolumn"
    type="plone.app.portlets.tests.test_configuration.ITestColumn"/>
 <portlet title="Test portlet" addview="portlets.test.Test"
    description="A test portlet"/>
 <assignment name="test.portlet6" category="group" key="Reviewers"
    manager="test.testcolumn" type="portlets.test.Test">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet4" category="content_type" key="Folder"
    manager="test.testcolumn" type="portlets.test.Test">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet5" category="content_type" key="Folder"
    manager="test.testcolumn" type="portlets.test.Test">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet3" category="context" key="/"
    manager="test.testcolumn" type="portlets.test.Test">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet2" category="context" key="/"
    manager="test.testcolumn" type="portlets.test.Test">
  <property name="test_bool">True</property>
  <property name="test_tuple"/>
  <property name="test_text">Test prop 2</property>
 </assignment>
 <assignment name="test.portlet1" category="context" key="/"
    manager="test.testcolumn" type="portlets.test.Test">
  <property name="test_bool">False</property>
  <property name="test_tuple"/>
  <property name="test_text">Test pröp 1</property>
 </assignment>
 <blacklist category="user" location="/" manager="test.testcolumn"
    status="acquire"/>
 <blacklist category="group" location="/" manager="test.testcolumn"
    status="show"/>
 <blacklist category="content_type" location="/" manager="test.testcolumn"
    status="block"/>
 <blacklist category="context" location="/" manager="test.testcolumn"
    status="acquire"/>
</portlets>
"""

        body = handler.body
        self.assertEquals(expected.strip(), body.strip(), body)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCML))
    suite.addTest(makeSuite(TestGenericSetup))
    return suite
