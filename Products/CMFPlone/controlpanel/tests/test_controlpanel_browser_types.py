from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
import unittest


class TypesControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the types control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.types_url = "%s/@@content-controlpanel" % self.portal_url
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )

    def test_types_control_panel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Editing').click()

    def test_standard_type_select(self):
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.assertIn('content-controlpanel', self.browser.url)

    def test_standard_type_cancel(self):
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getControl('Cancel').click()
        self.assertIn('@@overview-controlpanel', self.browser.url)

    def test_standard_type_allow_commenting(self):
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.browser.getControl('Allow comments').selected = True
        self.browser.getControl('Save').click()

        # Check if settings got saved correctly
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.assertIn('Globally addable', self.browser.contents)
        self.assertIn('Allow comments', self.browser.contents)
        self.assertEqual(
            self.browser.getControl('Allow comments').selected,
            True
        )
        self.assertIn('Visible in searches', self.browser.contents)
        self.assertIn(
            '<input id="redirect_links" type="checkbox" class="noborder"'
            ' name="redirect_links:boolean" checked="checked" />',
            self.browser.contents)
        self.assertIn(
            '<label for="redirect_links">Redirect immediately to link target',
            self.browser.contents
        )

    def test_standard_types_redirect_links(self):
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.browser.getControl(
            'Redirect immediately to link target'
        ).selected = True
        self.browser.getControl('Save').click()

        # Check if settings got saved correctly
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.assertTrue(
            'Redirect immediately to link target' in self.browser.contents
        )
        self.assertEqual(
            self.browser.getControl(
                'Redirect immediately to link target').selected,
            True
        )

    def test_set_no_default_workflow(self):
        # references http://dev.plone.org/plone/ticket/11901
        self.browser.open(self.types_url)
        self.browser.getControl(name="new_workflow").value = ['[none]']
        self.browser.getControl(name="form.button.Save").click()

        # Check that setting No workflow as default workflow doesn't break
        # break editing types
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.assertIn('Globally addable', self.browser.contents)
        self.assertIn('Allow comments', self.browser.contents)
        self.assertIn('Visible in searches', self.browser.contents)

    def test_disable_versioning_removes_behavior(self):
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Document']
        self.browser.getForm(action=self.types_url).submit()
        self.browser.getControl(name='versionpolicy').value = ['off']
        self.browser.getControl(name="form.button.Save").click()

        portal_types = self.portal.portal_types
        doc_type = portal_types.Document
        self.assertTrue(
            'plone.versioning'
            not in doc_type.behaviors)  # noqa

    def test_enable_versioning_behavior_on_document(self):
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Document']
        self.browser.getForm(action=self.types_url).submit()
        self.browser.getControl(name='versionpolicy').value = ['off']
        self.browser.getControl(name="form.button.Save").click()

        portal_types = self.portal.portal_types
        doc_type = portal_types.Document
        self.assertTrue(
            'plone.versioning'
            not in doc_type.behaviors)  # noqa

        self.browser.getControl(name='versionpolicy').value = ['manual']
        self.browser.getControl(name="form.button.Save").click()

        self.assertTrue(
            'plone.versioning'
            in doc_type.behaviors)

    def test_enable_versioning_behavior_on_file(self):
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['File']
        self.browser.getForm(action=self.types_url).submit()
        self.browser.getControl(name='versionpolicy').value = ['off']
        self.browser.getForm(action=self.types_url).submit()

        portal_types = self.portal.portal_types
        file_type = portal_types.File

        # File has no Versioning and no Locking on default, but needs it
        self.assertTrue(
            'plone.versioning'
            not in file_type.behaviors)  # noqa
        self.assertTrue(
            'plone.locking'
            not in file_type.behaviors)  # noqa

        self.browser.getControl(name='versionpolicy').value = ['manual']
        self.browser.getControl('Save').click()

        self.assertTrue(
            'plone.versioning'
            in file_type.behaviors)
        self.assertTrue(
            'plone.locking'
            in file_type.behaviors)

    def test_dont_update_settings_when_switch_types(self):
        # First of all, set a default
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.browser.getControl(
            'Redirect immediately to link target'
        ).selected = True
        self.browser.getControl('Save').click()

        # Then switch the type
        self.browser.getControl(name='type_id').value = ['Document']
        self.browser.getForm(action=self.types_url).submit()
        self.assertFalse(
            'Redirect immediately to link target' in self.browser.contents
        )

        # Go back to the link, and check the value
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()

        self.assertTrue(
            'Redirect immediately to link target' in self.browser.contents
        )
        self.assertEqual(
            self.browser.getControl(
                'Redirect immediately to link target').selected,
            True
        )

    def test_dont_update_redirect_links_when_not_in_link_settings(self):
        # First of all, set a default
        self.browser.open(self.types_url)
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()
        self.browser.getControl(
            'Redirect immediately to link target'
        ).selected = True
        self.browser.getControl('Save').click()

        # Then switch the type
        self.browser.getControl(name='type_id').value = ['Document']
        self.browser.getForm(action=self.types_url).submit()
        self.assertFalse(
            'Redirect immediately to link target' in self.browser.contents
        )
        self.browser.getControl('Save').click()

        # Go back to the link, and check the value
        self.browser.getControl(name='type_id').value = ['Link']
        self.browser.getForm(action=self.types_url).submit()

        self.assertTrue(
            'Redirect immediately to link target' in self.browser.contents
        )
        self.assertEqual(
            self.browser.getControl(
                'Redirect immediately to link target').selected,
            True
        )
