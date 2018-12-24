from Products.CMFPlone.interfaces.controlpanel import validate_email
import unittest


class MailControlPanelValidateEmailTest(unittest.TestCase):

    def test_validate_email_from_address(self):

    	self.assertTrue(
    		validate_email('uwaiszaki104@gmail.com')
    		)