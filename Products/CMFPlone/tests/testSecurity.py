# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from Testing.makerequest import makerequest
from zExceptions import NotFound
from zExceptions import Unauthorized

import re
import six
import transaction
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
        self.assertEqual(302, res.status)
        self.assertTrue(res.headers['location'].startswith(
            'http://nohost/plone/acl_users/credentials_cookie_auth/require_login'))

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

    @unittest.skip('Delete after move to ATContentTypes')
    def test_gtbn_faux_archetypes_tool(self):
        from Products.CMFCore.utils import FauxArchetypeTool
        from Products.CMFPlone.utils import getToolByName
        self.portal.portal_factory.archetype_tool = FauxArchetypeTool(
            self.portal.archetype_tool)
        self.assertEqual(self.portal.portal_factory.archetype_tool, getToolByName(
            self.portal.portal_factory, 'archetype_tool'))

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

    @unittest.skip('Delete after move to ATContentTypes')
    def test_at_download(self):
        self.setRoles(['Manager'])
        self.portal.portal_workflow.setChainForPortalTypes(
            ['File'], 'plone_workflow')
        self.portal.invokeFactory('File', 'test')
        self.portal.portal_workflow.doActionFor(self.portal.test, 'publish')

        # give it a more restricted read_permission
        self.portal.test.Schema()['file'].read_permission = 'Manage portal'

        # make sure at_download disallows even though the user has View
        # permission
        res = self.publish('/plone/test/at_download/file')
        self.assertEqual(res.status, 302)
        self.assertTrue(res.headers['location'].startswith(
            'http://nohost/plone/acl_users/credentials_cookie_auth/require_login'))

    @unittest.skip('Delete after move to ATContentTypes')
    def test_ftp(self):
        self.setRoles(['Manager', 'Owner'])
        self.portal.REQUEST.PARENTS = [self.app]
        res = self.portal.news.manage_FTPlist(self.portal.REQUEST)
        self.assertTrue(isinstance(res, six.string_types))
        self.portal.portal_workflow.doActionFor(self.portal.news, 'hide')
        self.setRoles(['Member'])
        from zExceptions import Unauthorized
        self.assertRaises(
            Unauthorized, self.portal.news.manage_FTPlist, self.portal.REQUEST)

    def test_atat_does_not_return_anything(self):
        res = self.publish('/plone/@@')
        self.assertEqual(404, res.status)

    @unittest.skip('Delete after move to ATContentTypes')
    def test_go_back(self):
        res = self.publish(
            '/plone/front-page/go_back?last_referer=http://${request}',
            basic=SITE_OWNER_NAME + ':' + SITE_OWNER_PASSWORD)
        # This used to show the request as location, so something like:
        # http://<h3>form</h3><table>... and then all kinds of data from the
        # request.  This was fixed in PloneHotfix20121106.  For this request
        # you then got redirected to url http://${request} which your browser
        # obviously does not know how to handle.
        #
        # In PloneHotfix20160830 this fix was kept, but additionally Plone
        # refuses to redirect to external sites by default.
        self.assertEqual(302, res.status)
        self.assertEqual(res.headers['location'],
                         self.portal.absolute_url() + '/front-page')

    def test_getFolderContents(self):
        res = self.publish('/plone/getFolderContents')
        self.assertEqual(403, res.status)

    def test_translate(self):
        res = self.publish('/plone/translate?msgid=foo')
        self.assertEqual(403, res.status)

    def test_utranslate(self):
        res = self.publish('/plone/utranslate?msgid=foo')
        self.assertEqual(403, res.status)

    @unittest.skip('Delete after move to ATContentTypes')
    def test_createObject(self):
        res = self.publish('/plone/createObject?type_name=File&id=${foo}')
        self.assertEqual(302, res.status)
        self.assertTrue(
            res.headers['location'].startswith(
                'http://nohost/plone/portal_factory/File/${foo}/'
                'edit?_authenticator='
            )
        )

    def test_formatColumns(self):
        # formatColumns is unused and was removed
        res = self.publish('/plone/formatColumns?items:list=')
        self.assertIn(res.status, [403, 404])


class TestFunctional(unittest.TestCase):
    # The class above is rather old-style.
    # Let's try a more modern approach, with a layer.
    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def get_admin_browser(self):
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        browser.addHeader(
            "Authorization",
            "Basic {0}:{1}".format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        return browser

    def test_plonetool(self):
        base_url = self.layer["portal"].absolute_url() + "/plone_utils"
        browser = self.get_admin_browser()
        method_names = (
            "addPortalMessage",
            "browserDefault",
            "getReviewStateTitleFor",
            "portal_utf8",
            "urlparse",
            "urlunparse",
            "utf8_portal",
            "getOwnerName",
            "normalizeString",
            "getEmptyTitle",
        )
        for method_name in method_names:
            with self.assertRaises(NotFound):
                browser.open(base_url + "/" + method_name)

    def test_hotfix_20160419(self):
        """Test old hotfix.

        CMFPlone has patches/publishing.py, containing
        the publishing patch from Products.PloneHotfix20160419.
        This avoids publishing some methods inherited from Zope or CMF,
        which upstream does not want to fix, considering it no problem
        to have these methods available.  I can imagine that.
        But in Plone we have decided otherwise.

        Problem: the patch did not work on Python 3.
        This was fixed in hotfix 20210518.
        """
        portal = self.layer["portal"]
        portal.invokeFactory("Document", "doc")
        transaction.commit()
        portal_url = portal.absolute_url()
        doc_url = portal.doc.absolute_url()
        browser = self.get_admin_browser()
        method_names = (
            "EffectiveDate",
            "ExpirationDate",
            "getAttributes",
            "getChildNodes",
            "getFirstChild",
            "getLastChild",
            "getLayout",
            "getNextSibling",
            "getNodeName",
            "getNodeType",
            "getNodeValue",
            "getOwnerDocument",
            "getParentNode",
            "getPhysicalPath",
            "getPreviousSibling",
            "getTagName",
            "hasChildNodes",
            "Type",
            # From PropertyManager:
            "getProperty",
            "propertyValues",
            "propertyItems",
            "propertyMap",
            "hasProperty",
            "getPropertyType",
            "propertyIds",
            "propertyLabel",
            "propertyDescription",
        )
        for method_name in method_names:
            with self.assertRaises(NotFound):
                browser.open(portal_url + "/" + method_name)
            with self.assertRaises(NotFound):
                browser.open(doc_url + "/" + method_name)

    def test_quick_installer_security(self):
        # Products.CMFQuickInstallerTool has a fix.
        # But CMFPlone overrides the tool class, so let's check.
        portal = self.layer["portal"]
        qi = getToolByName(portal, "portal_quickinstaller", None)
        if qi is None:
            return

        # Make sure we are anonymous.
        logout()
        logout()
        # Unrestricted traversal should work, restricted not.
        qi = portal.unrestrictedTraverse("portal_quickinstaller")
        with self.assertRaises(Unauthorized):
            portal.restrictedTraverse("portal_quickinstaller")
        for obj_id in qi.objectIds():
            qi.unrestrictedTraverse(obj_id)
            with self.assertRaises(Unauthorized):
                qi.restrictedTraverse(obj_id)

        # Authenticated with role Manager, we can view whatever we want.
        login(portal, SITE_OWNER_NAME)
        qi = portal.unrestrictedTraverse("portal_quickinstaller")
        qi = portal.restrictedTraverse("portal_quickinstaller")
        for obj_id in qi.objectIds():
            qi.unrestrictedTraverse(obj_id)
            qi.restrictedTraverse(obj_id)
