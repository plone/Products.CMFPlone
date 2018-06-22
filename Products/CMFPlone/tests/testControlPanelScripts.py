# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zExceptions import Forbidden


class TestPrefsUserManage(PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 0
        self.setupAuthenticator()

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({
            'fullname': fullname,
            'email': email,
            'last_login_time': DateTime(last_login_time), })

    def test_ploneChangePasswordPostOnly(self):
        self.login(TEST_USER_NAME)
        self.setRequestMethod('GET')
        self.assertRaises(
            Forbidden,
            self.portal.plone_change_password,
            current=TEST_USER_PASSWORD,
            password=TEST_USER_PASSWORD,
            password_confirm=TEST_USER_PASSWORD
        )


class TestAccessControlPanelScripts(PloneTestCase):
    '''Yipee, functional tests'''

    def afterSetUp(self):
        self.portal_path = self.portal.absolute_url(1)
        self.basic_auth = '%s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def testUserInformation(self):
        '''Test access to user details.'''
        response = self.publish('%s/@@user-information?userid=%s' %
                                (self.portal_path, TEST_USER_ID),
                                self.basic_auth)

        self.assertEqual(response.getStatus(), 200)

    def testUserPreferences(self):
        '''Test access to user details.'''
        response = self.publish('%s/@@user-preferences?userid=%s' %
                                (self.portal_path, TEST_USER_ID),
                                self.basic_auth)

        self.assertEqual(response.getStatus(), 200)
