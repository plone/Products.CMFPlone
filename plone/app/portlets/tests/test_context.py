from plone.app.portlets.tests.base import PortletsTestCase

from plone.portlets.interfaces import IPortletContext

from Testing.ZopeTestCase import user_name


class TestBasicContext(PortletsTestCase):

    def testParent(self):
        ctx = IPortletContext(self.folder)
        self.failUnless(ctx.getParent() is self.folder.aq_parent)

    def testGlobalsNoGroups(self):
        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 3)
        self.assertEquals(g[0], ('content_type', 'Folder'))
        self.assertEquals(g[1], ('user', user_name))

    def testGlobalsWithSingleGroup(self):

        group = self.portal.portal_groups.getGroupById('Reviewers')
        self.setRoles(('Manager', ))
        group.addMember(user_name)
        self.setRoles(('Member', ))

        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 4)
        self.assertEquals(g[0], ('content_type', 'Folder'))
        self.assertEquals(g[1], ('user', user_name))
        self.assertEquals(g[3], ('group', 'Reviewers'))

    def testGlobalsWithMultipleGroup(self):

        self.setRoles(('Manager', ))
        group = self.portal.portal_groups.getGroupById('Reviewers')
        group.addMember(user_name)
        group = self.portal.portal_groups.getGroupById('Administrators')
        group.addMember(user_name)
        self.setRoles(('Member', ))

        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 5)
        self.assertEquals(g[0], ('content_type', 'Folder'))
        self.assertEquals(g[1], ('user', user_name))
        self.assertEquals(g[2], ('group', 'Administrators'))
        self.assertEquals(g[4], ('group', 'Reviewers'))

    def testAnonymous(self):
        self.logout()
        ctx = IPortletContext(self.folder)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 2)
        self.assertEquals(g[0], ('content_type', 'Folder'))
        self.assertEquals(g[1], ('user', 'Anonymous User'))


class TestPortalRootContext(PortletsTestCase):

    def testParent(self):
        ctx = IPortletContext(self.portal)
        self.failUnless(ctx.getParent() is None)

    def testGlobalsNoGroups(self):
        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 3)
        self.assertEquals(g[0], ('content_type', 'Plone Site'))
        self.assertEquals(g[1], ('user', user_name))

    def testGlobalsWithSingleGroup(self):

        group = self.portal.portal_groups.getGroupById('Reviewers')
        self.setRoles(('Manager', ))
        group.addMember(user_name)
        self.setRoles(('Member', ))

        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 4)
        self.assertEquals(g[0], ('content_type', 'Plone Site'))
        self.assertEquals(g[1], ('user', user_name))
        self.assertEquals(g[3], ('group', 'Reviewers'))

    def testGlobalsWithMultipleGroup(self):

        self.setRoles(('Manager', ))
        group = self.portal.portal_groups.getGroupById('Reviewers')
        group.addMember(user_name)
        group = self.portal.portal_groups.getGroupById('Administrators')
        group.addMember(user_name)
        self.setRoles(('Member', ))

        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 5)
        self.assertEquals(g[0], ('content_type', 'Plone Site'))
        self.assertEquals(g[1], ('user', user_name))
        self.assertEquals(g[2], ('group', 'Administrators'))
        self.assertEquals(g[4], ('group', 'Reviewers'))

    def testAnonymous(self):
        self.logout()
        ctx = IPortletContext(self.portal)
        g = ctx.globalPortletCategories()
        self.assertEquals(len(g), 2)
        self.assertEquals(g[0], ('content_type', 'Plone Site'))
        self.assertEquals(g[1], ('user', 'Anonymous User'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBasicContext))
    suite.addTest(makeSuite(TestPortalRootContext))
    return suite
