from AccessControl.ZopeGuards import guarded_getattr
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zExceptions import Unauthorized


BAD_ATTR_STR = """
<p tal:content="python:'class of {0} is {0.__class__}'.format(context)" />
"""
BAD_ATTR_UNICODE = """
<p tal:content="python:u'class of {0} is {0.__class__}'.format(context)" />
"""
BAD_KEY_STR = """
<p tal:content="python:'access by key: {0[secret]}'.format(context)" />
"""
BAD_KEY_UNICODE = """
<p tal:content="python:u'access by key: {0[secret]}'.format(context)" />
"""
BAD_ITEM_STR = """
<p tal:content="python:'access by item: {0[0]}'.format(context)" />
"""
BAD_ITEM_UNICODE = """
<p tal:content="python:u'access by item: {0[0]}'.format(context)" />
"""
GOOD_STR = '<p tal:content="python:(\'%s\' % context).lower()" />'
GOOD_UNICODE = '<p tal:content="python:(\'%s\' % context).lower()" />'
# Attribute access is not completely forbidden, it is simply checked.
GOOD_FORMAT_ATTR_STR = """
<p tal:content="python:'title of {0} is {0.title}'.format(context)" />
"""
GOOD_FORMAT_ATTR_UNICODE = """
<p tal:content="python:u'title of {0} is {0.title}'.format(context)" />
"""
AQ_TEST = """
<p tal:content="python:\'parent of {0} is {0.aq_parent}\'.format(context)" />
"""


def noop(context=None):
    return lambda: context


def hack_pt(pt, context=None):
    # hacks to avoid getting error in pt_render.
    pt.getPhysicalRoot = noop()
    pt._getContext = noop(context)
    pt._getContainer = noop(context)
    pt.context = context


def create_private_document(portal, _id):
    setRoles(portal, TEST_USER_ID, ['Manager'])
    login(portal, TEST_USER_NAME)
    wf_tool = portal.portal_workflow
    wf_tool.setChainForPortalTypes(
        ['Document'], 'simple_publication_workflow')
    portal.invokeFactory('Document', _id)
    setRoles(portal, TEST_USER_ID, ['Member'])
    logout()
    return getattr(portal, _id)


class UnauthorizedSecurityPolicy:
    """Policy which denies every access."""

    def validate(self, *args, **kw):
        from AccessControl.unauthorized import Unauthorized
        raise Unauthorized('Nothing is allowed!')


class TestSafeFormatter(PloneTestCase):
    """The the safe formatter.

    This is from PloneHotfix20170117 and PloneHotfix20171128.
    """

    def test_cook_zope2_page_templates_bad_attr_str(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', BAD_ATTR_STR)
        hack_pt(pt)
        self.assertRaises(Unauthorized, pt.pt_render)
        hack_pt(pt, context=self.portal)
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_cook_zope2_page_templates_bad_attr_unicode(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', BAD_ATTR_UNICODE)
        hack_pt(pt)
        self.assertRaises(Unauthorized, pt.pt_render)
        hack_pt(pt, context=self.portal)
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_cook_zope2_page_templates_good_str(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', GOOD_STR)
        hack_pt(pt)
        self.assertEqual(pt.pt_render().strip(), '<p>none</p>')
        hack_pt(pt, context=self.portal)
        self.assertEqual(
            pt.pt_render().strip(), '<p>&lt;plonesite at plone&gt;</p>')

    def test_cook_zope2_page_templates_good_unicode(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', str(GOOD_UNICODE))
        hack_pt(pt)
        self.assertEqual(pt.pt_render().strip(), '<p>none</p>')
        hack_pt(pt, self.portal)
        self.assertEqual(
            pt.pt_render().strip(), '<p>&lt;plonesite at plone&gt;</p>')

    def test_cook_zope2_page_templates_good_format_attr_str(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', GOOD_FORMAT_ATTR_STR)
        hack_pt(pt, self.portal)
        self.assertEqual(
            pt.pt_render().strip(),
            '<p>title of &lt;PloneSite at plone&gt; is Welcome to Plone</p>')

    def test_cook_zope2_page_templates_good_format_attr_unicode(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', GOOD_FORMAT_ATTR_UNICODE)
        hack_pt(pt, self.portal)
        self.assertEqual(
            pt.pt_render().strip(),
            '<p>title of &lt;PloneSite at plone&gt; is Welcome to Plone</p>')

    def test_access_to_private_content_not_allowed_via_rich_text(self):
        try:
            from plone.app.textfield.value import RichTextValue
        except ImportError:
            return
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        foobar = create_private_document(self.portal, 'foobar')
        login(self.portal, TEST_USER_NAME)
        foobar.text = RichTextValue('Secret.', 'text/plain', 'text/html')
        self.assertEqual(
            self.portal.portal_workflow.getInfoFor(foobar, 'review_state'),
            'private')

        # Check that guarded_getattr is happy for the current user.
        self.assertEqual(guarded_getattr(self.portal, 'foobar'), foobar)
        self.assertEqual(
            guarded_getattr(self.portal.foobar, 'text'), foobar.text)
        # Access to text.output may be more restricted than access to the
        # text object itself, but this makes no sense, so we switch that
        # off in this test.
        # self.assertRaises(
        #     Unauthorized, guarded_getattr, self.portal.foobar.text, 'output')
        self.portal.foobar.text.__allow_access_to_unprotected_subobjects__ = 1
        self.assertEqual(
            guarded_getattr(self.portal.foobar.text, 'output'),
            '<p>Secret.</p>')
        TEMPLATE = '<p tal:content="structure python:%s" />'
        pt = ZopePageTemplate(
            'mytemplate', TEMPLATE %
            "'access {0.foobar.text.output}'.format(context)")
        hack_pt(pt, context=self.portal)
        self.assertEqual(pt.pt_render(), '<p>access <p>Secret.</p></p>')

        # Check the same for anonymous.
        logout()
        self.assertRaises(
            Unauthorized, guarded_getattr, self.portal, 'foobar')
        self.assertRaises(
            Unauthorized, guarded_getattr, self.portal.foobar, 'text')
        # *If* somehow anonymous can access the text, then we have allowed
        # access to the output as well.
        self.assertEqual(
            guarded_getattr(self.portal.foobar.text, 'output'),
            '<p>Secret.</p>')
        # But for the template anonymous would need access to everything,
        # which rightly fails.
        self.assertRaises(Unauthorized, pt.pt_render)

        # Test the simpler access without str.format for the current user.
        login(self.portal, TEST_USER_NAME)
        pt = ZopePageTemplate(
            'mytemplate', TEMPLATE %
            "context.foobar.text.output")
        hack_pt(pt, context=self.portal)
        self.assertEqual(pt.pt_render(), '<p><p>Secret.</p></p>')

        # and for anonymous
        logout()
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_access_to_private_content_not_allowed_in_any_way(self):
        # This is a more general version of the rich text one.
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        foobar = create_private_document(self.portal, 'foobar')
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(
            self.portal.portal_workflow.getInfoFor(foobar, 'review_state'),
            'private')
        TEMPLATE = '<p tal:content="structure python:%s" />'

        # attribute access
        # If access to context.foobar.Title was allowed, it would still only
        # say 'bound method DexterityContent.Title', without giving the actual title,
        # but there may be other attributes that give worse info.
        pt = ZopePageTemplate(
            'mytemplate', TEMPLATE %
            "'access {0.foobar.Title}'.format(context)")
        hack_pt(pt, context=self.portal)
        login(self.portal, TEST_USER_NAME)
        method_name = 'DexterityContent.Title'
        self.assertEqual(
            pt.pt_render(),
            '<p>access <bound method %s of '
            '<Document at /plone/foobar>></p>' % method_name)
        logout()
        self.assertRaises(Unauthorized, pt.pt_render)

        # key access
        pt = ZopePageTemplate(
            'mytemplate', TEMPLATE %
            "'{0[foobar]}'.format(context)")
        hack_pt(pt, context=self.portal)
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(
            pt.pt_render(),
            '<p><Document at foobar></p>')
        logout()
        self.assertRaises(Unauthorized, pt.pt_render)

        # Prepare a list so we can test item access.
        self.portal.testlist = [foobar]
        pt = ZopePageTemplate(
            'mytemplate', TEMPLATE %
            "'{0.testlist}'.format(context)")
        hack_pt(pt, context=self.portal)
        # If you have such a list, you *can* see an id.
        self.assertEqual(
            pt.pt_render(),
            '<p>[<Document at /plone/foobar>]</p>')
        # But you cannot access an item.
        pt = ZopePageTemplate(
            'mytemplate', TEMPLATE %
            "'{0.testlist[0]}'.format(context)")
        hack_pt(pt, context=self.portal)
        self.assertRaises(Unauthorized, pt.pt_render)
        # except as authenticated user
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(
            pt.pt_render(),
            '<p><Document at foobar></p>')

    # Zope 3 templates are always file system templates.  So we actually have
    # no problems allowing str.format there.

    def test_cook_zope3_page_templates_normal(self):
        from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
        # Note: on Plone 3.3 this is actually a ZopeTwoPageTemplateFile.
        pt = ViewPageTemplateFile('normal_zope3_page_template.pt')
        hack_pt(pt)
        # Need to pass a namespace.
        namespace = {'context': self.portal}
        self.assertEqual(
            pt.pt_render(namespace).strip(),
            '<p>&lt;plonesite at plone&gt;</p>\n'
            '<p>&lt;PLONESITE AT PLONE&gt;</p>')

    def test_cook_zope3_page_templates_using_format(self):
        from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
        # Note: on Plone 3.3 this is actually a ZopeTwoPageTemplateFile.
        pt = ViewPageTemplateFile('using_format_zope3_page_template.pt')
        hack_pt(pt)
        # Need to pass a namespace.
        namespace = {'context': self.portal}
        self.assertEqual(
            pt.pt_render(namespace).strip(),
            "<p>class of &lt;plonesite at plone&gt; is "
            "&lt;class 'products.cmfplone.portal.plonesite'&gt;</p>\n"
            "<p>CLASS OF &lt;PLONESITE AT PLONE&gt; IS "
            "&lt;CLASS 'PRODUCTS.CMFPLONE.PORTAL.PLONESITE'&gt;</p>\n"
            "<p>{'foo': 42} has foo=42</p>\n"
            "<p>{'foo': 42} has foo=42</p>\n"
            "<p>['ni'] has first item ni</p>\n"
            "<p>['ni'] has first item ni</p>"
        )


class TestFunctionalSafeFormatter(PloneTestCase):
    """Functional tests for the safe formatter.

    This is from PloneHotfix20170117 and PloneHotfix20171128.
    """

    def test_safe_format_properly_applied(self):
        from AccessControl.SimpleObjectPolicies import ContainerAssertions
        import types
        ca = ContainerAssertions
        self.assertTrue(str in ca)
        self.assertTrue(isinstance(ca[str], dict))
        self.assertTrue('format' in ca[str])
        string_rule = ca[str]['format']
        self.assertTrue(isinstance(string_rule, types.FunctionType))
        # Take less steps for unicode.
        unicode_rule = ca[str]['format']
        self.assertTrue(isinstance(unicode_rule, types.FunctionType))
        self.assertEqual(string_rule, unicode_rule)

    def test_standard_error_message(self):
        # In Plone 5.0 standard_error_message.py has:
        # if "text/html" not in context.REQUEST.getHeader('Accept', ''):
        #    return '{{"error_type": "{0:s}"}}'.format(error_type)
        #
        # So if there is an error and the request does not accept html, then
        # str.format is used.  We don't want this to fail with an Unauthorized.
        # For good measure we check this in Plone 4.3 too.

        response = self.publish(
            '/plone/standard_error_message',
            env={'HTTP_ACCEPT': 'application/json'})

        # This should *not* return a 302 Unauthorized.  We expect a 404.  Or
        # really a 200, because we explicitly call the standard_error_message
        # page and this is correctly rendered.
        self.assertTrue(response.status in (200, 404))
        # We expect a json string back.
        self.assertTrue(response.body, '{"error_type": "None"}')

    def test_cook_zope2_page_templates_bad_key_str(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', BAD_KEY_STR)
        hack_pt(pt, self.portal)
        create_private_document(self.portal, 'secret')
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(
            pt.pt_render().replace('ATDocument', 'Document'),
            '<p>access by key: &lt;Document at secret&gt;</p>')
        logout()
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_cook_zope2_page_templates_bad_key_unicode(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', BAD_KEY_UNICODE)
        hack_pt(pt, self.portal)
        create_private_document(self.portal, 'secret')
        login(self.portal, TEST_USER_NAME)
        self.assertEqual(
            pt.pt_render().replace('ATDocument', 'Document'),
            '<p>access by key: &lt;Document at secret&gt;</p>')
        logout()
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_cook_zope2_page_templates_bad_item_str(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        secret = create_private_document(self.portal, 'secret')
        login(self.portal, TEST_USER_NAME)
        self.portal.testlist = [secret]
        pt = ZopePageTemplate('mytemplate', BAD_ITEM_STR)
        hack_pt(pt, self.portal.testlist)
        self.assertEqual(
            pt.pt_render().replace('ATDocument', 'Document'),
            '<p>access by item: &lt;Document at secret&gt;</p>')
        logout()
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_cook_zope2_page_templates_bad_item_unicode(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        secret = create_private_document(self.portal, 'secret')
        login(self.portal, TEST_USER_NAME)
        self.portal.testlist = [secret]
        pt = ZopePageTemplate('mytemplate', BAD_ITEM_UNICODE)
        hack_pt(pt, self.portal.testlist)
        self.assertEqual(
            pt.pt_render().replace('ATDocument', 'Document'),
            '<p>access by item: &lt;Document at secret&gt;</p>')
        logout()
        self.assertRaises(Unauthorized, pt.pt_render)

    def assert_is_checked_via_security_manager(self, pt_content):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        from AccessControl.SecurityManager import setSecurityPolicy
        from AccessControl.SecurityManagement import noSecurityManager

        pt = ZopePageTemplate('mytemplate', pt_content)
        noSecurityManager()
        old_security_policy = setSecurityPolicy(UnauthorizedSecurityPolicy())
        try:
            hack_pt(pt, context=self.portal)
            self.assertRaises(Unauthorized, pt.pt_render)
        finally:
            setSecurityPolicy(old_security_policy)

    def test_getattr_access_is_checked_via_security_manager(self):
        self.assert_is_checked_via_security_manager(
            """<p tal:content="python:'{0.acl_users}'.format(context)" />""")

    def test_getitem_access_is_checked_via_security_manager(self):
        self.assert_is_checked_via_security_manager(
            """<p tal:content="python:'{c[acl_users]}'.format(c=context)" />"""
        )

    def test_key_access_is_checked_via_security_manager(self):
        self.assert_is_checked_via_security_manager(
            """<p tal:content="python:'{c[0]}'.format(c=[context])" />"""
        )
