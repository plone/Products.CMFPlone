# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING  # noqa: E501
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


class ZMITests(unittest.TestCase):
    """Basic tests of ZMI management screens
    """

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_manage(self):
        url = 'manage'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_main(self):
        url = 'manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_components(self):
        url = 'manage_components'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_propertiesForm(self):
        url = 'manage_propertiesForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_UndoForm(self):
        url = 'manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_owner(self):
        url = 'manage_owner'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_interfaces(self):
        url = 'manage_interfaces'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_findForm(self):
        url = 'manage_findForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_acl_users(self):
        url = 'acl_users/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_caching_policy_manager(self):
        url = 'caching_policy_manager/manage_cachingPolicies'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_content_type_registry(self):
        url = 'content_type_registry/manage_predicates'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_error_log(self):
        url = 'error_log/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_HTTPCache(self):
        url = 'HTTPCache/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_MailHost(self):
        url = 'MailHost/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_mimetypes_registry(self):
        url = 'mimetypes_registry/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_plone_utils(self):
        url = 'plone_utils/manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_actions(self):
        url = 'portal_actions/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_archivist(self):
        url = 'portal_archivist/manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_catalog(self):
        url = 'portal_catalog/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_css(self):
        url = 'portal_css/manage_cssForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_diff(self):
        url = 'portal_diff/manage_difftypes'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_form_controller(self):
        url = 'portal_form_controller/manage_overview'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_groupdata(self):
        url = 'portal_groupdata/manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_groups(self):
        url = 'portal_groups/manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_historiesstorage(self):
        url = 'portal_historiesstorage/storageStatistics'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_historyidhandler(self):
        url = 'portal_historyidhandler/manage_queryObject'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_javascripts(self):
        url = 'portal_javascripts/manage_jsForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_memberdata(self):
        url = 'portal_memberdata/manage_overview'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_membership(self):
        url = 'portal_membership/manage_mapRoles'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_modifier(self):
        url = 'portal_modifier/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_password_reset(self):
        url = 'portal_password_reset/manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_properties(self):
        url = 'portal_properties/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_purgepolicy(self):
        url = 'portal_purgepolicy/manage_propertiesForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_quickinstaller(self):
        url = 'portal_quickinstaller/manage_installProductsForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_referencefactories(self):
        url = 'portal_referencefactories/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_registration(self):
        url = 'portal_registration/manage_overview'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_registry(self):
        url = 'portal_registry/manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_repository(self):
        url = 'portal_repository/manage_owner'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_resources(self):
        url = 'portal_resources/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_setup(self):
        url = 'portal_setup/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_skins(self):
        url = 'portal_skins/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_transforms(self):
        url = 'portal_transforms/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_types(self):
        url = 'portal_types/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_uidannotation(self):
        url = 'portal_uidannotation/manage_propertiesForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_uidgenerator(self):
        url = 'portal_uidgenerator/manage_UndoForm'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_uidhandler(self):
        url = 'portal_uidhandler/manage_queryObject'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_view_customizations(self):
        url = 'portal_view_customizations/registrations.html'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_portal_workflow(self):
        url = 'portal_workflow/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_RAMCache(self):
        url = 'RAMCache/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_ResourceRegistryCache(self):
        url = 'ResourceRegistryCache/manage_main'
        view = self.portal.restrictedTraverse(url)
        self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_manage_access(self):
        """manage_access cannot be travesed to directly
        """
        view = getattr(self.portal, '_normal_manage_access')
        self.assertTrue(view(), msg='manage_access is broken')

    def test_portal_controlpanel(self):
        # portal_controlpanel/manage_editActionsForm
        controlpanel = self.portal.restrictedTraverse('portal_controlpanel')
        view = controlpanel._actions_form
        self.assertTrue(
            view(),
            msg='portal_controlpanel/manage_editActionsForm is broken')
