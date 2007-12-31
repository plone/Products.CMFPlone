from zope.component import getUtilitiesFor
from zope.interface import Interface

from plone.portlets.interfaces import IPortletType

from Products.CMFPlone.migrations.migration_util import loadMigrationProfile


def three1_alpha1(portal):
    """3.0.x -> 3.1-alpha1
    """

    out = []
    
    migratePortletTypeRegistrations(portal, out)

    return out


def migratePortletTypeRegistrations(portal, out):
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0.4-3.1a1')
    
    out.append("Ran GenericSetup profile to migrate default portlet types " \
       "to support multiple portlet manager interfaces and limit many " \
       "default portlet types to left, right, and dashboard columns.")
    
    for name, portletType in getUtilitiesFor(IPortletType):
        if portletType.for_ is None:
            portletType.for_ = [Interface]
        elif type(portletType.for_) not in [tuple, list]:
            portletType.for_ = [portletType.for_]
    
    out.append("Migrated any non default portlet types to new " \
      "to support multiple portlet manager interfaces.")
