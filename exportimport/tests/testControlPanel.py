#
# Exportimport adapter tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase

from zope.app.component.hooks import setHooks, setSite
from zope.component import getSiteManager
from Products.CMFActionIcons.interfaces import IActionIconsTool
from Products.CMFPlone.interfaces import IControlPanel
from Products.CMFPlone.PloneControlPanel import PloneControlPanel
from Products.CMFPlone.setuphandlers import PloneGenerator
from OFS.Folder import Folder

_CONTROLPANEL_XML = """\
<?xml version="1.0"?>
<object name="portal_controlpanel" meta_type="Plone Control Panel Tool">
 <configlet title="Add/Remove Products" action_id="QuickInstaller"
    appId="QuickInstaller" category="Plone" condition_expr=""
    url_expr="string:${portal_url}/prefs_install_products_form"
    visible="True">
  <permission>Manage portal</permission>
 </configlet>
</object>
"""


class DummyActionIconsTool(Folder):

    id = 'portal_actionicons'
    meta_type = 'Dummy Action Icons Tool'

    def queryActionInfo(self, category, action_id, default=None, context=None):
        pass


class ControlPanelXMLAdapterTests(BodyAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFPlone.exportimport.controlpanel \
                    import ControlPanelXMLAdapter
        return ControlPanelXMLAdapter

    def _populate(self, obj):
        obj.registerConfiglet( id='QuickInstaller'
                             , name='Add/Remove Products'
                             , action='string:${portal_url}/prefs_install_products_form'
                             , permission='Manage portal'
                             , category='Plone'
                             , visible=True
                             , appId='QuickInstaller'
                             )

    def setUp(self):
        setHooks()
        self.site = Folder('site')
        gen = PloneGenerator()
        gen.enableSite(self.site)
        setSite(self.site)
        sm = getSiteManager()
        self.site.portal_actionicons = DummyActionIconsTool()
        sm.registerUtility(self.site.portal_actionicons, IActionIconsTool)
        self.site.portal_control_panel = PloneControlPanel()
        sm.registerUtility(self.site.portal_control_panel, IControlPanel)

        self._obj = self.site.portal_control_panel
        self._BODY = _CONTROLPANEL_XML


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ControlPanelXMLAdapterTests))
    return suite

if __name__ == '__main__':
    framework()

