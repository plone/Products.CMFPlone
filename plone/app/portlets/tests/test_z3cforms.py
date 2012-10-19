import time
from z3c.form import field
from zope import schema
from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from zope.interface import implements
from zope.site.hooks import setHooks, setSite

from Products.PloneTestCase.layer import PloneSite

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer
from plone.app.portlets.portlets import base
from plone.app.portlets.browser import z3cformhelper
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
# BBB Zope 2.12
try:
    from Zope2.App import zcml
    from OFS import metaconfigure
    zcml # pyflakes
    metaconfigure
except ImportError:
    from Products.Five import zcml
    from Products.Five import fiveconfigure as metaconfigure


class Iz3cPortlet(IPortletDataProvider):
    """A dummy z3c portlet.
    """

    foo = schema.Text(title=u"Foo")


class Assignment(base.Assignment):

    implements(Iz3cPortlet)

    def __init__(self, foo=u''):
        self.foo = foo


class Renderer(base.Renderer):

    def render(self, context, request):
        return self.data.foo


class AddForm(z3cformhelper.AddForm):

    fields = field.Fields(Iz3cPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(z3cformhelper.EditForm):

    fields = field.Fields(Iz3cPortlet)


zcml_string = """\
<configure xmlns="http://namespaces.zope.org/zope"
           xmlns:plone="http://namespaces.plone.org/plone"
           xmlns:genericsetup="http://namespaces.zope.org/genericsetup"
           package="plone.app.portlets"
           i18n_domain="test">

    <plone:portlet
        name="portlet.z3cTest"
        interface="plone.app.portlets.tests.test_z3cforms.Iz3cPortlet"
        assignment="plone.app.portlets.tests.test_z3cforms.Assignment"
        renderer="plone.app.portlets.tests.test_z3cforms.Renderer"
        addview="plone.app.portlets.tests.test_z3cforms.AddForm"
        editview="plone.app.portlets.tests.test_z3cforms.EditForm"
        />

    <genericsetup:registerProfile
        name="z3ctesting"
        title="plone.app.portlets z3c testing"
        description="Used for testing only"
        directory="tests/profiles/z3ctesting"
        for="Products.CMFCore.interfaces.ISiteRoot"
        provides="Products.GenericSetup.interfaces.EXTENSION"
        />

</configure>
"""


class z3cPortletZCMLLayer(PloneSite):

    @classmethod
    def setUp(cls):
        metaconfigure.debug_mode = True
        zcml.load_string(zcml_string)
        metaconfigure.debug_mode = False

    @classmethod
    def tearDown(cls):
        pass


class TestPortlet(PortletsTestCase):

    layer = z3cPortletZCMLLayer

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager', ))
        portal_setup = self.portal.portal_setup
        # wait a bit or we get duplicate ids on import
        time.sleep(0.2)
        portal_setup.runAllImportStepsFromProfile('profile-plone.app.portlets:z3ctesting')

    def testInterfaces(self):
        portlet = Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlet.z3cTest')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]

        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'foo': 'bar'})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST
        mapping['foo'] = Assignment(foo='bar')
        editview = queryMultiAdapter((mapping['foo'], request), name='edit', default=None)
        self.assertTrue(editview is not None)

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = Assignment(foo='bar')
        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, Renderer))
        self.assertEqual(renderer.render(context, request), 'bar')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    return suite
