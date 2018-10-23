# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zExceptions import Forbidden

import unittest


class TestPrefsUserManage(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 0
        # self.setupAuthenticator()

    def test_ploneChangePasswordPostOnly(self):
        # self.login(TEST_USER_NAME)
        self.layer['request'].method = 'GET'
        with self.assertRaises(Forbidden):
            self.portal.plone_change_password(
                current=TEST_USER_PASSWORD,
                password=TEST_USER_PASSWORD,
                password_confirm=TEST_USER_PASSWORD,
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
