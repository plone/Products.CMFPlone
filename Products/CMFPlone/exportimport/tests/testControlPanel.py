from OFS.Folder import Folder
from plone.base.interfaces import IControlPanel
from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase
from Products.CMFPlone.PloneControlPanel import PloneControlPanel
from zope.component import provideAdapter
from zope.component import provideUtility


_CONTROLPANEL_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<object name="portal_controlpanel" meta_type="Plone Control Panel Tool">
 <configlet title="Add/Remove Products" action_id="QuickInstaller"
    appId="QuickInstaller" category="Plone" condition_expr=""
    icon_expr="string:${portal_url}/product_icon.png"
    url_expr="string:${portal_url}/prefs_install_products_form"
    visible="True">
  <permission>Manage portal</permission>
 </configlet>
</object>
"""


class ControlPanelXMLAdapterTests(BodyAdapterTestCase):
    def _getTargetClass(self):
        from Products.CMFPlone.exportimport.controlpanel import ControlPanelXMLAdapter

        return ControlPanelXMLAdapter

    def _populate(self, obj):
        obj.registerConfiglet(
            id="QuickInstaller",
            name="Add/Remove Products",
            action="string:${portal_url}/prefs_install_products_form",
            permission="Manage portal",
            category="Plone",
            visible=True,
            appId="QuickInstaller",
            icon_expr="string:${portal_url}/product_icon.png",
        )

    def setUp(self):
        from Products.GenericSetup.interfaces import IBody
        from Products.GenericSetup.interfaces import ISetupEnviron

        self.site = Folder("site")
        self.site.portal_control_panel = PloneControlPanel()
        provideUtility(self.site.portal_control_panel, IControlPanel)
        provideAdapter(self._getTargetClass(), (IControlPanel, ISetupEnviron), IBody)
        self._obj = self.site.portal_control_panel
        self._BODY = _CONTROLPANEL_XML


def test_suite():
    import unittest

    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromTestCase(ControlPanelXMLAdapterTests),
    ))
