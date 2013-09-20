# logged_in.cpy tests

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
            self.assertNotEqual(self.membership.getHomeFolder(), None)

    def testLoggedInSetsLoginTime(self):
        now = DateTime()
        member = self.membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty('login_time')) < now)
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty('login_time')) >= now)

    def testLoggedInSetsLastLoginTime(self):
        now = DateTime()
        member = self.membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty('last_login_time')) < now)
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty('last_login_time')) >= now)

    def testLoggedInSetsLastLoginTimeIfMemberLacksSetOwnPropertiesPermission(self):
        # If members lack the "Set own properties" permission, they should
        # still be able to log in, and their login times should be set.
        now = DateTime()
        self.portal.manage_permission(SetOwnProperties, ['Manager'], acquire=0)
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty('last_login_time')) >= now)

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
        self.assertTrue(
			DateTime(member.getProperty('login_time')) > login_time)

    def testInitialLoginTimeWithString(self):
        member = self.membership.getAuthenticatedMember()
        # Realize the login_time is not string but DateTime
        self.assertTrue(isinstance(member.getProperty('login_time'), DateTime))
        self.assertEqual(member.getProperty('login_time').Date(), '2000/01/01')

        # Update login_time into string
        today = DateTime().Date()
        member.setProperties(login_time=today)
        self.assertTrue(isinstance(member.getProperty('login_time'), str))
        self.assertEqual(member.getProperty('login_time'), today)

        # Loggin in set login_time with DateTime
        self.portal.logged_in()
        member = self.membership.getAuthenticatedMember()
        self.assertTrue(isinstance(member.getProperty('login_time'), DateTime))
        self.assertTrue(member.getProperty('login_time') > DateTime(today))
