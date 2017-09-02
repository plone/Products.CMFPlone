# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING  # noqa: E501
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest

ZMI_URLS = [
    'manage',
    'manage_main',
    'manage_components',
    'manage_propertiesForm',
    'manage_UndoForm',
    'manage_owner',
    'manage_interfaces',
    'manage_findForm',
    'acl_users/manage_main',
    'caching_policy_manager/manage_cachingPolicies',
    'content_type_registry/manage_predicates',
    'error_log/manage_main',
    'HTTPCache/manage_main',
    'MailHost/manage_main',
    'mimetypes_registry/manage_main',
    'plone_utils/manage_UndoForm',
    'portal_actions/manage_main',
    'portal_archivist/manage_UndoForm',
    'portal_catalog/manage_main',
    'portal_css/manage_cssForm',
    'portal_diff/manage_difftypes',
    'portal_form_controller/manage_overview',
    'portal_groupdata/manage_UndoForm',
    'portal_groups/manage_UndoForm',
    'portal_historiesstorage/storageStatistics',
    'portal_historyidhandler/manage_queryObject',
    'portal_javascripts/manage_jsForm',
    'portal_memberdata/manage_overview',
    'portal_membership/manage_mapRoles',
    'portal_modifier/manage_main',
    'portal_password_reset/manage_UndoForm',
    'portal_properties/manage_main',
    'portal_purgepolicy/manage_propertiesForm',
    'portal_quickinstaller/manage_installProductsForm',
    'portal_referencefactories/manage_main',
    'portal_registration/manage_overview',
    'portal_registry/manage_UndoForm',
    'portal_repository/manage_owner',
    'portal_resources/manage_main',
    'portal_setup/manage_main',
    'portal_skins/manage_main',
    'portal_transforms/manage_main',
    'portal_types/manage_main',
    'portal_uidannotation/manage_propertiesForm',
    'portal_uidgenerator/manage_UndoForm',
    'portal_uidhandler/manage_queryObject',
    'portal_view_customizations/registrations.html',
    'portal_workflow/manage_main',
    'RAMCache/manage_main',
    'ResourceRegistryCache/manage_main',
    'translation_service/manage_UndoForm',
]

ZMI_ATTRIBUTES = [
    '_normal_manage_access',  # /manage_access
]


class ZMITests(unittest.TestCase):
    """Basic tests of ZMI management screens
    """

    layer = PLONE_APP_CONTENTTYPES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_zmi_management_screens(self):
        for url in ZMI_URLS:
            view = self.portal.restrictedTraverse(url)
            self.assertTrue(view(), msg='{0} is broken'.format(url))

    def test_zmi_management_screens_attributes(self):
        """Some urls like manage_access cannot be travesed to directly
        """
        for attr in ZMI_ATTRIBUTES:
            view = getattr(self.portal, attr)
            self.assertTrue(view(), msg='{0} is broken'.format(attr))

        # More special casess
        controlpanel = self.portal.restrictedTraverse('portal_controlpanel')
        view = controlpanel._actions_form
        self.assertTrue(
            view(),
            msg='portal_controlpanel/manage_editActionsForm is broken')
