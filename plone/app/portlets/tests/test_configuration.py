# -*- coding: utf-8 -*-

import time
import transaction

from zope.i18nmessageid import Message
from zope.interface import Interface
from zope.component import getUtility, queryUtility, getMultiAdapter
from zope.component.interfaces import IFactory

from zope.component import getSiteManager
from zope.site.hooks import setSite, setHooks

from plone.app.portlets.tests.base import PortletsTestCase

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.browser import BrowserView

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.context import TarballExportContext
from Products.GenericSetup.tests.common import DummyImportContext

from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase

from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentSettings

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.portlets.manager import PortletManager
from plone.portlets.utils import registerPortletType

from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.interfaces import IColumn

from plone.app.portlets.browser.adding import PortletAdding
from plone.app.portlets.utils import assignment_mapping_from_key

from plone.app.portlets.exportimport.portlets import importPortlets


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
           package="plone.app.portlets"
           i18n_domain="test">

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

        # needed to avoid deep and magic five.localsitemanager wrapping problems
        setSite(portal)
        setHooks()

        portal_setup = portal.portal_setup
        # wait a bit or we get duplicate ids on import
        time.sleep(1)

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

    def disabled_testPortletTypeRegistered(self):
        portlet_type = getUtility(IPortletType, name=u"portlets.test.Test")
        self.assertEquals('portlets.test.Test', portlet_type.addview)
        self.assertEquals([Interface], portlet_type.for_)
        # XXX Missing i18n support in the exportimport code
        self.failUnless(isinstance(portlet_type.title, Message),
                        "Portlet title should be a Message instance")
        self.failUnless(isinstance(portlet_type.description, Message),
                        "Portlet description should be a Message instance")
        self.assertEquals(u"title_test_portlet", portlet_type.title)
        self.assertEquals(u"description_test_portlet", portlet_type.description)
        self.assertEquals(u"Test portlet", portlet_type.title.default)
        self.assertEquals(u"A test portlet", portlet_type.description.default)
        self.assertEquals(u"plone", portlet_type.title.domain)
        self.assertEquals(u"plone", portlet_type.description.domain)

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

    def testAssignmentSettings(self):
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        assignment = mapping['test.portlet1']
        settings = IPortletAssignmentSettings(assignment)
        self.failUnless(settings.get('visible', True))

        assignment = mapping['test.portlet2']
        settings = IPortletAssignmentSettings(assignment)
        self.failIf(settings.get('visible', True))

    def testAssignmentRoot(self):
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        self.assertEquals(3, len(mapping))

        # No assignment in /news subfolder
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/news")
        self.assertEquals(0, len(mapping))

        context = DummyImportContext(self.portal, purge=False)
        context._files['portlets.xml'] = """<?xml version="1.0"?>
            <portlets>
                <assignment
                    manager="test.testcolumn"
                    category="context"
                    key="/news"
                    type="portlets.test.Test"
                    name="test.portlet4"
                    />
            </portlets>
        """
        importPortlets(context)

        # Still 3 portlets in the root
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        self.assertEquals(3, len(mapping))

        # but 1 extra in the /news subfolder
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/news")
        self.assertEquals(1, len(mapping))

    def testAssignmentRemoval(self):
        portal_setup = self.portal.portal_setup

        # wait a bit or we get duplicate ids on import
        time.sleep(1)
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

    def testAssignmentPurging(self):
        # initially there should be 3 assignments on the root
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        self.assertEquals(3, len(mapping))

        context = DummyImportContext(self.portal, purge=False)
        context._files['portlets.xml'] = """<?xml version="1.0"?>
            <portlets>
                <assignment
                    manager="test.testcolumn"
                    category="context"
                    key="/"
                    purge="True"
                    />
            </portlets>
        """
        importPortlets(context)

        # now they should be gone
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        self.assertEquals(0, len(mapping))

        # group assignments should still be there
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=GROUP_CATEGORY, key="Reviewers")
        self.assertEquals(1, len(mapping))

        # and be purgable
        context = DummyImportContext(self.portal, purge=False)
        context._files['portlets.xml'] = """<?xml version="1.0"?>
            <portlets>
                <assignment
                    manager="test.testcolumn"
                    category="group"
                    key="Reviewers"
                    purge="True"
                    />
            </portlets>
        """
        importPortlets(context)

        # now they should be gone
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=GROUP_CATEGORY, key="Reviewers")
        self.assertEquals(0, len(mapping))

        # also content type assignments should still be there
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTENT_TYPE_CATEGORY, key="Folder")
        self.assertEquals(2, len(mapping))

        # and be purgable
        context = DummyImportContext(self.portal, purge=False)
        context._files['portlets.xml'] = """<?xml version="1.0"?>
            <portlets>
                <assignment
                    manager="test.testcolumn"
                    category="content_type"
                    key="Folder"
                    purge="True"
                    />
            </portlets>
        """
        importPortlets(context)

        # now they should be gone
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTENT_TYPE_CATEGORY, key="Folder")
        self.assertEquals(0, len(mapping))

    def testBlacklisting(self):
        manager = getUtility(IPortletManager, name=u"test.testcolumn")

        if 'news' in self.portal.objectIds():
            news = self.portal['news']

            assignable = getMultiAdapter(
                (news, manager), ILocalPortletAssignmentManager)

            self.assertEquals(
                True, assignable.getBlacklistStatus(CONTEXT_CATEGORY))
            self.assertEquals(
                False, assignable.getBlacklistStatus(GROUP_CATEGORY))
            self.assertEquals(
                None, assignable.getBlacklistStatus(CONTENT_TYPE_CATEGORY))

    def testPurgeMethod(self):
        sm = getSiteManager()
        context = TarballExportContext(self.portal.portal_setup)
        handler = getMultiAdapter((sm, context), IBody, name=u'plone.portlets')
        handler._purgePortlets()

        manager = queryUtility(IPortletManager, name=u"test.testcolumn")
        self.assertEquals(None, manager)

    def testPurge(self):
        manager = queryUtility(IPortletManager, name=u"test.testcolumn")
        self.assertNotEquals(None, manager)

        context = DummyImportContext(self.portal, purge=False)
        context._files['portlets.xml'] = """<?xml version="1.0"?>
            <portlets purge="True">
            </portlets>
        """
        importPortlets(context)

        manager = queryUtility(IPortletManager, name=u"test.testcolumn")
        self.assertEquals(None, manager)

    def testManagerRemove(self):
        manager = queryUtility(IPortletManager, name=u"test.testcolumn")
        self.assertNotEquals(None, manager)

        context = DummyImportContext(self.portal, purge=False)
        context._files['portlets.xml'] = """<?xml version="1.0"?>
            <portlets>
                <portletmanager
                    name="test.testcolumn"
                    remove="True"
                    />
            </portlets>
        """
        importPortlets(context)

        manager = queryUtility(IPortletManager, name=u"test.testcolumn")
        self.assertEquals(None, manager)

    def testManagerPurge(self):
        context = DummyImportContext(self.portal, purge=False)
        context._files['portlets.xml'] = """<?xml version="1.0"?>
            <portlets>
                <portletmanager
                    name="test.testcolumn"
                    purge="True"
                    />
            </portlets>
        """
        importPortlets(context)

        self.assertRaises(KeyError,
                          assignment_mapping_from_key,
                          self.portal, manager_name=u"test.testcolumn",
                          category=GROUP_CATEGORY, key="Reviewers")

        self.assertRaises(KeyError,
                          assignment_mapping_from_key,
                          self.portal, manager_name=u"test.testcolumn",
                          category=CONTENT_TYPE_CATEGORY, key="Folder")

        # context assignment at the root are purged as well
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=u"test.testcolumn", category=CONTEXT_CATEGORY, key="/")
        self.assertEquals(0, len(mapping))

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
 <portletmanager name="test.testcolumn2"
    type="plone.app.portlets.tests.test_configuration.ITestColumn"/>
 <portletmanager name="test.testcolumn"
    type="plone.app.portlets.tests.test_configuration.ITestColumn"/>
 <portlet title="Test portlet" addview="portlets.test.Test"
    description="A test portlet"/>
 <assignment name="test.portlet6" category="group" key="Reviewers"
    manager="test.testcolumn" type="portlets.test.Test" visible="True">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet4" category="content_type" key="Folder"
    manager="test.testcolumn" type="portlets.test.Test" visible="True">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet5" category="content_type" key="Folder"
    manager="test.testcolumn" type="portlets.test.Test" visible="True">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet3" category="context" key="/"
    manager="test.testcolumn" type="portlets.test.Test" visible="True">
  <property name="test_bool"/>
  <property name="test_tuple"/>
  <property name="test_text"/>
 </assignment>
 <assignment name="test.portlet2" category="context" key="/"
    manager="test.testcolumn" type="portlets.test.Test" visible="False">
  <property name="test_bool">True</property>
  <property name="test_tuple"/>
  <property name="test_text">Test prop 2</property>
 </assignment>
 <assignment name="test.portlet1" category="context" key="/"
    manager="test.testcolumn" type="portlets.test.Test" visible="True">
  <property name="test_bool">False</property>
  <property name="test_tuple"/>
  <property name="test_text">Test pröp 1</property>
 </assignment>
 <assignment name="navigation" category="context" key="/"
    manager="test.testcolumn2" type="portlets.Navigation" visible="True">
  <property name="topLevel">1</property>
  <property name="currentFolderOnly">False</property>
  <property name="name"></property>
  <property name="includeTop">False</property>
  <property name="bottomLevel">0</property>
  <property name="root"></property>
 </assignment>
 <blacklist category="user" location="/" manager="test.testcolumn"
    status="acquire"/>
 <blacklist category="group" location="/" manager="test.testcolumn"
    status="show"/>
 <blacklist category="content_type" location="/" manager="test.testcolumn"
    status="block"/>
 <blacklist category="context" location="/" manager="test.testcolumn"
    status="acquire"/>
 <blacklist category="user" location="/" manager="test.testcolumn2"
    status="acquire"/>
 <blacklist category="group" location="/" manager="test.testcolumn2"
    status="acquire"/>
 <blacklist category="content_type" location="/" manager="test.testcolumn2"
    status="acquire"/>
 <blacklist category="context" location="/" manager="test.testcolumn2"
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
