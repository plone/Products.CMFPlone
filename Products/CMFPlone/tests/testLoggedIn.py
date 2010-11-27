#
# logged_in.cpy tests
#

from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.permissions import SetOwnProperties
from DateTime import DateTime
from time import sleep


class TestLogin(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('member', 'secret', ['Member'], [])
        self.login('member')

    def testLoggedInCreatesMemberArea(self):
        if self.membership.memberareaCreationFlag == 'True':
            self.assertEqual(self.membership.getHomeFolder(), None)
            self.portal.logged_in()
            self.failIfEqual(self.membership.getHomeFolder(), None)

    def testLoggedInSetsLoginTime(self):
        now = DateTime()
        member = self.membership.getAuthenticatedMember()
        self.failUnless(DateTime(member.getProperty('login_time')) < now)
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        self.failUnless(DateTime(member.getProperty('login_time')) >= now)

    def testLoggedInSetsLastLoginTime(self):
        now = DateTime()
        member = self.membership.getAuthenticatedMember()
        self.failUnless(DateTime(member.getProperty('last_login_time')) < now)
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        self.failUnless(DateTime(member.getProperty('last_login_time')) >= now)

    def testLoggedInSetsLastLoginTimeIfMemberLacksSetOwnPropertiesPermission(self):
        # If members lack the "Set own properties" permission, they should still
        # be able to log in, and their login times should be set.
        now = DateTime()
        self.portal.manage_permission(SetOwnProperties, ['Manager'], acquire=0)
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        self.failUnless(DateTime(member.getProperty('last_login_time')) >= now)

    def testInitialLoginTimeDoesChange(self):
        member = self.membership.getAuthenticatedMember()
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        login_time = DateTime(member.getProperty('login_time'))
        # Log in again later
        sleep(0.2)
        self.portal.logged_in()
        # login_time did change
        member = self.membership.getAuthenticatedMember()
        self.failUnless(DateTime(member.getProperty('login_time')) > login_time)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLogin))
    return suite
