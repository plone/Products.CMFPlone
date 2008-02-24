from zope.component import getUtilitiesFor
from zope.interface import Interface

from plone.portlets.interfaces import IPortletType

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.migrations.migration_util import loadMigrationProfile

def three0_alpha1(portal):
    """3.0.6 -> 3.1alpha1
    """
    out = []

    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0.6-3.1alpha1')

    addBrowserLayer(portal, out)
    migratePortletTypeRegistrations(portal, out)

    return out

def addBrowserLayer(portal, out):
    qi=getToolByName(portal, "portal_quickinstaller")
    if not qi.isProductInstalled("plone.browserlayer"):
        qi.installProduct("plone.browserlayer", locked=True)
        out.append("Installed plone.browserlayer")

def migratePortletTypeRegistrations(portal, out):
    for name, portletType in getUtilitiesFor(IPortletType):
        if portletType.for_ is None:
            portletType.for_ = [Interface]
        elif type(portletType.for_) is not list:
            portletType.for_ = [portletType.for_]
    
    out.append("Migrated portlet types to support multiple " + \
      "portlet manager interfaces.")
