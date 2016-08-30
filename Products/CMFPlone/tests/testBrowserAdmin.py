import urlparse
import os
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.permissions import ModifyPortalContent
from Products.PluggableAuthService.interfaces.plugins import IChallengePlugin

from AccessControl import Permissions
from AccessControl import getSecurityManager
portal_owner = PloneTestCase.portal_owner
default_password = PloneTestCase.default_password


class TestPloneRootLoginURL(PloneTestCase.FunctionalTestCase):

    def test_normal_redirect(self):
        url = '@@plone-root-login?came_from=%s' % self.portal.absolute_url()
        response = self.publish(
            url,
            basic='%s:%s' % (portal_owner, default_password),
            handle_errors=False,
        )
        self.assertNotEqual(response.headers.get('location'), None)
        self.assertEqual(response.headers.get('location'),
                         self.portal.absolute_url())

    def test_attacker_redirect(self):
        attackers = (
            'http://attacker.com',
            '\\attacker.com',
        )
        for attacker in attackers:
            url = '@@plone-root-login?came_from=%s' % attacker
            response = self.publish(
                url,
                basic='%s:%s' % (portal_owner, default_password),
                handle_errors=False,
            )
            self.assertNotEqual(response.headers.get('location'), None)
            self.assertNotEqual(response.headers.get('location'), attacker)
            # Whatever the url is, it starts with the Zope root url.
            self.assertTrue(response.headers.get('location').startswith(
                self.app.absolute_url()), response.headers.get('location'))
