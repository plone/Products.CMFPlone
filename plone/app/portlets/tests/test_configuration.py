from transaction import commit

from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import IFactory

from plone.app.portlets.tests.base import PortletsTestCase

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.browser import BrowserView

from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase

from plone.portlets.interfaces import IPortletType, IPortletRenderer, IPortletManager
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.manager import PortletManager

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
    test = schema.TextLine(title=u"Test")

class TestAssignment(base.Assignment):
    implements(ITestPortlet)
    test = u""
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
        
        commit()
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
        self.assertEquals(None, portlet_type.for_)
        
    def testAssignmentCreatedAndOrdered(self):
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        self.assertEquals(3, len(mapping))
        self.assertEquals(['test.portlet3', 'test.portlet2', 'test.portlet1'], list(mapping.keys()))
        
    def testAssignmentPropertiesSet(self):
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        assignment = mapping['test.portlet1']
        self.assertEquals('Test prop', assignment.test)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZCML))
    suite.addTest(makeSuite(TestGenericSetup))
    return suite
