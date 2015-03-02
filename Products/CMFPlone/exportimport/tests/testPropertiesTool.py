from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase
from Products.CMFPlone.PropertiesTool import PropertiesTool
from Products.CMFPlone.PropertiesTool import SimpleItemWithProperties
from zope.component import provideAdapter

_PROPERTYSHEET_XML = """\
<?xml version="1.0"?>
<object name="site_properties" meta_type="Plone Property Sheet">
 <property name="title">Site wide properties</property>
 <property name="displayPublicationDateInByline"
    type="boolean">True</property>
</object>
"""

_PROPERTIESTOOL_XML = """\
<?xml version="1.0"?>
<object name="portal_properties" meta_type="Plone Properties Tool">
 <object name="site_properties" meta_type="Plone Property Sheet">
  <property name="title">Site wide properties</property>
  <property name="displayPublicationDateInByline"
     type="boolean">True</property>
 </object>
</object>
"""


class PropertySheetXMLAdapterTests(BodyAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFPlone.exportimport.propertiestool \
            import SimpleItemWithPropertiesXMLAdapter
        return SimpleItemWithPropertiesXMLAdapter

    def _populate(self, obj):
        obj.manage_changeProperties(title='Site wide properties')
        obj.manage_addProperty(
            'displayPublicationDateInByline', True, 'boolean')

    def setUp(self):
        from Products.CMFPlone.interfaces import ISimpleItemWithProperties
        from Products.GenericSetup.interfaces import ISetupEnviron
        from Products.GenericSetup.interfaces import IBody
        provideAdapter(
            self._getTargetClass(),
            (ISimpleItemWithProperties, ISetupEnviron), IBody)

        self._obj = SimpleItemWithProperties('site_properties')
        self._BODY = _PROPERTYSHEET_XML


class PropertiesToolXMLAdapterTests(BodyAdapterTestCase):

    def _getTargetClass(self):
        from Products.CMFPlone.exportimport.propertiestool \
            import PlonePropertiesToolXMLAdapter
        return PlonePropertiesToolXMLAdapter

    def _populate(self, obj):
        obj._setObject('site_properties',
                       SimpleItemWithProperties('site_properties'))
        obj.site_properties.manage_changeProperties(
            title='Site wide properties')
        obj.site_properties.manage_addProperty(
            'displayPublicationDateInByline', True, 'boolean')

    def setUp(self):
        from Products.CMFPlone.exportimport.propertiestool \
            import SimpleItemWithPropertiesXMLAdapter
        from Products.CMFPlone.interfaces import IPropertiesTool
        from Products.CMFPlone.interfaces import ISimpleItemWithProperties
        from Products.GenericSetup.interfaces import ISetupEnviron
        from Products.GenericSetup.interfaces import IBody
        provideAdapter(
            self._getTargetClass(), (IPropertiesTool, ISetupEnviron), IBody)
        provideAdapter(
            SimpleItemWithPropertiesXMLAdapter,
            (ISimpleItemWithProperties, ISetupEnviron), IBody)

        self._obj = PropertiesTool()
        self._BODY = _PROPERTIESTOOL_XML


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(PropertySheetXMLAdapterTests))
    suite.addTest(makeSuite(PropertiesToolXMLAdapterTests))
    return suite
