from Acquisition import aq_base
from Testing.ZopeTestCase import user_name

from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setSite, setHooks

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.portlets.constants import USER_CATEGORY, CONTEXT_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.portlets import classic

from plone.app.portlets.tests.base import PortletsTestCase

from plone.app.portlets.utils import assignment_from_key

class TestAssignmentFromKey(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.manager = getUtility(IPortletManager, name=u'plone.leftcolumn')
        self.cat = self.manager[USER_CATEGORY]
        self.cat[user_name] = PortletAssignmentMapping(manager=u'plone.leftcolumn',
                                                       category=USER_CATEGORY,
                                                       name=user_name)

    def testGetPortletFromContext(self):
        mapping = getMultiAdapter((self.folder, self.manager,), IPortletAssignmentMapping)
        c = classic.Assignment()
        mapping['foo'] = c
        path = '/'.join(self.folder.getPhysicalPath())
        a = assignment_from_key(self.portal, u'plone.leftcolumn', CONTEXT_CATEGORY, path, 'foo')
        self.assertEquals(c, a)

    def testGetPortletFromUserCategory(self):
        c = classic.Assignment()
        self.cat[user_name]['foo'] = c
        a = assignment_from_key(self.portal, u'plone.leftcolumn', USER_CATEGORY, user_name, 'foo')
        self.assertEquals(c, a)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAssignmentFromKey))
    return suite
