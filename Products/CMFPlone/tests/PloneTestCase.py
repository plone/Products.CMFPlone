from plone.testing.zope import Browser
from plone.app.testing.bbb import PloneTestCase
from plone.app.testing import PLONE_SITE_ID as portal_name
from plone.app.testing import TEST_USER_ID as default_user
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD as default_password

from plone.protect.authenticator import AuthenticatorView
from re import match
import transaction

# We do not use these, but someone might import them.
portal_name, default_user  # pyflakes


class PloneTestCase(PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

    def setRequestMethod(self, method):
        self.app.REQUEST.set('REQUEST_METHOD', method)
        self.app.REQUEST.method = method

    def getAuthenticator(self):
        tag = AuthenticatorView('context', 'request').authenticator()
        pattern = r'<input .*name="(\w+)".*value="(\w+)"'
        return match(pattern, tag).groups()

    def setupAuthenticator(self):
        name, token = self.getAuthenticator()
        self.app.REQUEST.form[name] = token

    def getBrowser(self, loggedIn=True):
        transaction.commit()
        browser = Browser(self.app)
        if loggedIn:
            user = TEST_USER_NAME
            pwd = default_password
            browser.addHeader('Authorization', f'Basic {user}:{pwd}')
        return browser


class FunctionalTestCase(PloneTestCase):
    pass
