# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser

from zope.component import getMultiAdapter
from zope.component import getUtility

from Products.CMFPlone.interfaces import IMailSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

import unittest2 as unittest


class MailControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the mail control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_mail_controlpanel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Mail').click()

    def test_mail_controlpanel_backlink(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_mail_controlpanel_sidebar(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/@@overview-controlpanel')

    def test_mail_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="mail-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_mail_controlpanel_smtp_host(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.smtp_host').value = 'example.com'
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        self.assertEqual(settings.smtp_host, 'example.com')

    def test_mail_controlpanel_smtp_port(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.smtp_port').value = '88'
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        self.assertEqual(str(settings.smtp_port), '88')

    def test_mail_controlpanel_smtp_userid(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.smtp_userid').value = 'john@example.com'
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        self.assertEqual(settings.smtp_userid, 'john@example.com')

    def test_mail_controlpanel_smtp_pass(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.smtp_pass').value = 'secret'
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        self.assertEqual(settings.smtp_pass, 'secret')

    def test_mail_controlpanel_smtp_pass_keep_on_saving(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.smtp_userid').value = 'john@example.com'
        self.browser.getControl(
            name='form.widgets.smtp_pass').value = 'secret'
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()
        self.browser.getControl(name='form.buttons.save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        self.assertEqual(settings.smtp_pass, 'secret')

    def test_mail_controlpanel_email_from_name(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        self.assertEqual(settings.email_from_name, 'John')

    def test_mail_controlpanel_email_from_address(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        self.assertEqual(settings.email_from_address, 'john@example.com')

    def test_mail_controlpanel_contactinfo_page(self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        self.browser.open(
            "%s/contact-info" % self.portal_url)
        self.assertTrue(
            'Message' in self.browser.contents,
            u'Message exists not in the contact-info form!'
        )

    def test_controlpanel_overview_shows_no_unconfigured_mailhost_warning(
            self):
        self.browser.open(
            "%s/@@mail-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.email_from_name').value = 'John'
        self.browser.getControl(
            name='form.widgets.email_from_address').value = \
                'john@example.com'
        self.browser.getControl(name='form.buttons.save').click()

        self.browser.open(
            "%s/overview-controlpanel" % self.portal_url)
        self.assertFalse(
            'not configured a mail host' in self.browser.contents,
            u'There should not be a warning for unconfigured mailhost!'
        )

    def test_controlpanel_overview_shows_unconfigured_mailhost_warning(
            self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMailSchema, prefix="plone")
        settings.email_from_name = None
        settings.email_from_address = None
        self.browser.open(
            "%s/overview-controlpanel" % self.portal_url)
        self.assertTrue(
            'not configured a mail host' in self.browser.contents,
            u'There should be a warning for unconfigured mailhost!'
        )
