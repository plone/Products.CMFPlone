# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IMailSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import getAdapter

import unittest2 as unittest


class MailControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.mail_settings = registry.forInterface(
            IMailSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, IMailSchema))

    def test_get_smtp_host(self):
        self.assertEqual(
            getAdapter(self.portal, IMailSchema).smtp_host,
            u'localhost'
        )
        self.mail_settings.smtp_host = u'example.com'
        self.assertEquals(
            getAdapter(self.portal, IMailSchema).smtp_host,
            u'example.com'
        )

    def test_set_smtp_host(self):
        self.assertEquals(
            self.mail_settings.smtp_host,
            u'localhost'
        )
        getAdapter(self.portal, IMailSchema).smtp_host = u'example.com'
        self.assertEquals(
            self.mail_settings.smtp_host,
            u'example.com'
        )

    def test_get_smtp_port(self):
        self.assertEqual(
            getAdapter(self.portal, IMailSchema).smtp_port,
            25
        )
        self.mail_settings.smtp_port = 88
        self.assertEquals(
            getAdapter(self.portal, IMailSchema).smtp_port,
            88
        )

    def test_set_smtp_port(self):
        self.assertEquals(
            self.mail_settings.smtp_port,
            25
        )
        getAdapter(self.portal, IMailSchema).smtp_port = 88
        self.assertEquals(
            self.mail_settings.smtp_port,
            88
        )

    def test_get_smtp_userid(self):
        self.assertEqual(
            getAdapter(self.portal, IMailSchema).smtp_userid,
            None
        )
        self.mail_settings.smtp_userid = u'john@example.com'
        self.assertEquals(
            getAdapter(self.portal, IMailSchema).smtp_userid,
            u'john@example.com'
        )

    def test_set_smtp_userid(self):
        self.assertEquals(
            self.mail_settings.smtp_userid,
            None
        )
        getAdapter(self.portal, IMailSchema).smtp_userid = u'john@example.com'
        self.assertEquals(
            self.mail_settings.smtp_userid,
            u'john@example.com'
        )

    def test_get_smtp_pass(self):
        self.assertEqual(
            getAdapter(self.portal, IMailSchema).smtp_pass,
            None
        )
        self.mail_settings.smtp_pass = u'secret'
        self.assertEquals(
            getAdapter(self.portal, IMailSchema).smtp_pass,
            u'secret'
        )

    def test_set_smtp_pass(self):
        self.assertEquals(
            self.mail_settings.smtp_pass,
            None
        )
        getAdapter(self.portal, IMailSchema).smtp_pass = u'secret'
        self.assertEquals(
            self.mail_settings.smtp_pass,
            u'secret'
        )

    def test_get_email_from_name(self):
        self.assertEqual(
            getAdapter(self.portal, IMailSchema).email_from_name,
            None
        )
        self.mail_settings.email_from_name = u'John'
        self.assertEquals(
            getAdapter(self.portal, IMailSchema).email_from_name,
            u'John'
        )

    def test_set_email_from_name(self):
        self.assertEquals(
            self.mail_settings.email_from_name,
            None
        )
        getAdapter(self.portal, IMailSchema).email_from_name = u'John'
        self.assertEquals(
            self.mail_settings.email_from_name,
            u'John'
        )

    def test_get_email_from_address(self):
        self.assertEqual(
            getAdapter(self.portal, IMailSchema).email_from_address,
            None
        )
        self.mail_settings.email_from_address = 'john@example.com'
        self.assertEquals(
            getAdapter(self.portal, IMailSchema).email_from_address,
            'john@example.com'
        )

    def test_set_email_from_address(self):
        self.assertEquals(
            self.mail_settings.email_from_address,
            None
        )
        getAdapter(self.portal, IMailSchema).email_from_address = \
            'john@example.com'
        self.assertEquals(
            self.mail_settings.email_from_address,
            'john@example.com'
        )
