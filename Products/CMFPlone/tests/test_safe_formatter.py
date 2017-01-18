from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zExceptions import Unauthorized


BAD_STR = """
<p tal:content="python:'class of {0} is {0.__class__}'.format(context)" />
"""
BAD_UNICODE = """
<p tal:content="python:u'class of {0} is {0.__class__}'.format(context)" />
"""
GOOD_STR = '<p tal:content="python:(\'%s\' % context).lower()" />'
GOOD_UNICODE = '<p tal:content="python:(\'%s\' % context).lower()" />'
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


class TestSafeFormatter(PloneTestCase):
    """The the safe formatter.

    This is from PloneHotfix20170117.
    """

    def test_cook_zope2_page_templates_bad_str(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', BAD_STR)
        hack_pt(pt)
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_cook_zope2_page_templates_bad_unicode(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', BAD_UNICODE)
        hack_pt(pt)
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_cook_zope2_page_templates_good_str(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', GOOD_STR)
        hack_pt(pt)
        self.assertEqual(pt.pt_render().strip(), '<p>none</p>')

    def test_cook_zope2_page_templates_good_unicode(self):
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', unicode(GOOD_UNICODE))
        hack_pt(pt)
        self.assertEqual(pt.pt_render().strip(), '<p>none</p>')

    def test_cook_zope2_page_templates_aq_parent(self):
        # Accessing aq_parent should be allowed normally.
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        pt = ZopePageTemplate('mytemplate', AQ_TEST)
        hack_pt(pt, context=self.portal)
        self.assertEqual(
            pt.pt_render().strip(),
            u'<p>parent of &lt;PloneSite at plone&gt; is '
            u'&lt;Application at &gt;</p>')

    def test_access_to_private_content_not_allowed_via_rich_text(self):
        try:
            # This is only available for tests if we have plone.app.dexterity,
            # which in tests is by default only the case for Plone 5.
            from plone.app.textfield.value import RichTextValue
        except ImportError:
            return
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        wf_tool = self.portal.portal_workflow
        wf_tool.setChainForPortalTypes(
            ['Document'], 'simple_publication_workflow')
        self.portal.invokeFactory('Document', 'foobar')
        foobar = self.portal.foobar
        foobar.text = RichTextValue(u'Secret.', 'text/plain', 'text/html')
        self.assertEqual(
            self.portal.portal_workflow.getInfoFor(foobar, 'review_state'),
            'private')
        logout()
        pt = ZopePageTemplate('mytemplate', '''
<p tal:content="structure python:'access {0.foobar.text.output}'.format(context).lower()" />
''')  # noqa
        hack_pt(pt, context=self.portal)
        self.assertRaises(Unauthorized, pt.pt_render)

    def test_access_to_private_content_not_allowed_via_any_attribute(self):
        # This is a more general version of the rich text one.
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        wf_tool = self.portal.portal_workflow
        wf_tool.setChainForPortalTypes(
            ['Document'], 'simple_publication_workflow')
        self.portal.invokeFactory('Document', 'foobar')
        foobar = self.portal.foobar
        self.assertEqual(
            self.portal.portal_workflow.getInfoFor(foobar, 'review_state'),
            'private')
        logout()
        # If access to context.foobar.Title was allowed, it would still only
        # say 'bound method ATDocument.Title', without giving the actual title,
        # but there may be other attributes that give worse info.
        pt = ZopePageTemplate('mytemplate', '''
<p tal:content="structure python:'access {0.foobar.Title}'.format(context)" />
''')
        hack_pt(pt, context=self.portal)
        self.assertRaises(Unauthorized, pt.pt_render)

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
            u'<p>&lt;plonesite at plone&gt;</p>\n'
            u'<p>&lt;PLONESITE AT PLONE&gt;</p>')

    def test_cook_zope3_page_templates_using_format(self):
        from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
        # Note: on Plone 3.3 this is actually a ZopeTwoPageTemplateFile.
        pt = ViewPageTemplateFile('using_format_zope3_page_template.pt')
        hack_pt(pt)
        # Need to pass a namespace.
        namespace = {'context': self.portal}
        self.assertEqual(
            pt.pt_render(namespace).strip(),
            u"<p>class of &lt;plonesite at plone&gt; is "
            u"&lt;class 'products.cmfplone.portal.plonesite'&gt;</p>\n"
            u"<p>CLASS OF &lt;PLONESITE AT PLONE&gt; IS "
            u"&lt;CLASS 'PRODUCTS.CMFPLONE.PORTAL.PLONESITE'&gt;</p>")

    def test_standard_error_message(self):
        # In Plone 5.0 standard_error_message.py has:
        # if "text/html" not in context.REQUEST.getHeader('Accept', ''):
        #    return '{{"error_type": "{0:s}"}}'.format(error_type)
        #
        # So if there is an error and the request does not accept html, then
        # str.format is used.  We don't want this to fail with an Unauthorized.

        response = self.publish(
            '/plone/standard_error_message',
            env={'HTTP_ACCEPT': 'application/json'})

        # This should *not* return a 302 Unauthorized.  We expect a 404.  Or
        # really a 200, because we explicitly call the standard_error_message
        # page and this is correctly rendered.
        self.assertTrue(response.status in (200, 404))
        # We expect a json string back.
        self.assertTrue(response.body, '{"error_type": "None"}')

    def test_resource_registry_vector(self):
        for vector in ('less-variables.js', 'less-modify.js'):
            src = '''
class ctx:
  def format(self, *args, **kwargs):
    self.foo=context
    return "foo"

context.portal_registry['plone.lessvariables']['foo'] = ctx()
context.portal_registry['plone.lessvariables']['bar'] = "{foo.foo.__class__}"
js = context.restrictedTraverse("%s")
return js()
''' % vector
            from Products.PythonScripts.PythonScript import PythonScript
            script = PythonScript('evil')
            script._filepath = 'evil'
            script.write(src)
            self.portal.evil = script
            output = self.publish('/plone/evil')
            self.assertFalse(
                'Products.CMFPlone.Portal.PloneSite' in output.body)

    def test_positional_argument_regression(self):
        """
        to test http://bugs.python.org/issue13598 issue
        """
        from Products.CMFPlone.utils import SafeFormatter
        try:
            self.assertEquals(
                SafeFormatter('{} {}').safe_format('foo', 'bar'),
                'foo bar'
            )
        except ValueError:
            # On Python 2.6 you get:
            # ValueError: zero length field name in format
            pass

        self.assertEquals(
            SafeFormatter('{0} {1}').safe_format('foo', 'bar'),
            'foo bar'
        )
        self.assertEquals(
            SafeFormatter('{1} {0}').safe_format('foo', 'bar'),
            'bar foo'
        )
