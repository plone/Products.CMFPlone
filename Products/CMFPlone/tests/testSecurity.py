from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from Testing.makerequest import makerequest
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from zExceptions import Unauthorized

import re
import unittest


class TestAttackVectorsUnit(unittest.TestCase):

    def test_setHeader_drops_LF(self):
        from ZPublisher.HTTPResponse import HTTPResponse
        response = HTTPResponse()
        response.setHeader('Location',
                           'http://www.ietf.org/rfc/\nrfc2616.txt')
        self.assertEqual(response.headers['location'],
                         'http://www.ietf.org/rfc/rfc2616.txt')

    def test_PT_allow_module_not_available_in_RestrictedPython_1(self):
        src = '''
from AccessControl import Unauthorized
try:
    import Products.PlacelessTranslationService
except (ImportError, Unauthorized):
    raise AssertionError("Failed to import Products.PTS")
Products.PlacelessTranslationService.allow_module('os')
'''
        from Products.PythonScripts.PythonScript import PythonScript
        script = makerequest(PythonScript('fooscript'))
        script._filepath = 'fooscript'
        script.write(src)
        self.assertRaises((ImportError, Unauthorized), script)

    def test_PT_allow_module_not_available_in_RestrictedPython_2(self):
        src = '''
from Products.PlacelessTranslationService import allow_module
allow_module('os')
'''
        from Products.PythonScripts.PythonScript import PythonScript
        script = makerequest(PythonScript('barscript'))
        script._filepath = 'barscript'
        script.write(src)
        self.assertRaises((ImportError, Unauthorized), script)

    def test_get_request_var_or_attr_disallowed(self):
        import App.Undo
        self.assertFalse(hasattr(App.Undo.UndoSupport,
                                 'get_request_var_or_attr'))


class TestAttackVectorsFunctional(PloneTestCase):

    def test_gtbn_funcglobals(self):
        from Products.CMFPlone.utils import getToolByName
        try:
            getToolByName(self.assertTrue, '__globals__')['__builtins__']
        except TypeError:
            pass
        else:
            self.fail('getToolByName should block access to non CMF tools')

    def test_widget_traversal_1(self):
        res = self.publish(
            '/plone/@@discussion-settings/++widget++moderator_email')
        self.assertEqual(302, res.status)
        self.assertTrue(res.headers['location'].startswith(
            'http://nohost/plone/acl_users/credentials_cookie_auth/require_login'))

    def test_widget_traversal_2(self):
        res = self.publish(
            '/plone/@@discussion-settings/++widget++captcha/terms/field/interface/setTaggedValue?tag=cake&value=lovely')
        self.assertEqual(404, res.status)
        # self.assertTrue(res.headers['location'].startswith(
        #     'http://nohost/plone/acl_users/credentials_cookie_auth/require_login'))

    def test_registerConfiglet_1(self):
        VECTOR = "/plone/portal_controlpanel/registerConfiglet?id=cake&name=Cakey&action=woo&permission=View&icon_expr="
        res = self.publish(VECTOR)
        self.assertEqual(404, res.status)

    def test_registerConfiglet_2(self):
        VECTOR = "/plone/portal_controlpanel/registerConfiglet?id=cake&name=Cakey&action=woo&permission=View&icon_expr="
        self.publish(VECTOR)
        action_ids = [
            action.id for action in self.portal.portal_controlpanel._actions]
        self.assertTrue('cake' not in action_ids)

    def _get_authenticator(self, basic=None):
        url = '/plone/login_password'
        res = self.publish(url, basic=basic)
        m = re.search('name="_authenticator" value="([^"]*)"', res.body)
        if m:
            return m.group(1)
        return ''

    def test_searchForMembers(self):
        res = self.publish('/plone/portal_membership/searchForMembers')
        self.assertEqual(302, res.status)
        self.assertTrue(res.headers['location'].startswith(
            'http://nohost/plone/acl_users/credentials_cookie_auth/require_login'))

    def test_getMemberInfo(self):
        res = self.publish('/plone/portal_membership/getMemberInfo?id=admin')
        self.assertEqual(404, res.status)

    def test_queryCatalog(self):
        res = self.publish('/plone/news/aggregator/queryCatalog')
        self.assertEqual(404, res.status)

    def test_resolve_url(self):
        res = self.publish("/plone/uid_catalog/resolve_url?path=/evil")
        self.assertEqual(404, res.status)

    def test_atat_does_not_return_anything(self):
        res = self.publish('/plone/@@')
        self.assertEqual(404, res.status)

    def test_getFolderContents(self):
        res = self.publish('/plone/getFolderContents')
        self.assertEqual(403, res.status)

    def test_translate(self):
        res = self.publish('/plone/translate?msgid=foo')
        self.assertEqual(403, res.status)

    def test_utranslate(self):
        res = self.publish('/plone/utranslate?msgid=foo')
        self.assertEqual(403, res.status)

    def test_formatColumns(self):
        # formatColumns is unused and was removed
        res = self.publish('/plone/formatColumns?items:list=')
        self.assertIn(res.status, [403, 404])
