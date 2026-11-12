from plone.registry.interfaces import IRegistry
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getUtility
from zope.sendmail.mailer import SMTPMailer

import unittest


class TestMailerSettings(unittest.TestCase):
    """The SMTP mailer takes its settings from the mail control panel."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.registry = getUtility(IRegistry)
        self.registry["plone.smtp_host"] = "smtp.example.org"
        self.registry["plone.smtp_port"] = 465

    def test_settings(self):
        mailer = SMTPMailer()
        self.assertEqual(mailer.hostname, "smtp.example.org")
        self.assertEqual(mailer.port, 465)
        self.assertFalse(mailer.implicit_tls)

    def test_implicit_tls(self):
        self.registry["plone.smtp_implicit_tls"] = True
        self.assertTrue(SMTPMailer().implicit_tls)

    def test_implicit_tls_from_mailhost(self):
        # Switched on in the MailHost in the ZMI, it stays on.
        self.assertTrue(SMTPMailer(implicit_tls=True).implicit_tls)

    def test_without_implicit_tls_record(self):
        # A site that is not upgraded yet can still send mail.
        del self.registry.records["plone.smtp_implicit_tls"]
        mailer = SMTPMailer()
        self.assertEqual(mailer.hostname, "smtp.example.org")
        self.assertFalse(mailer.implicit_tls)
