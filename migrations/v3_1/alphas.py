from zope.component import getUtilitiesFor

from plone.portlets.interfaces import IPortletType


def three1_alpha1(portal):
    """3.0.x -> 3.1-alpha1
    """

    out = []
    
    migratePortletTypeRegistrations(portal, out)

    return out


def migratePortletTypeRegistrations(portal, out):
    for name, portletType in getUtilitiesFor(IPortletType):
        if portletType.for_ is None:
            portletType.for_ = []
        elif type(portletType.for_) not in [tuple, list]:
            portletType.for_ = [portletType.for_]
    
    out.append("Migrated portlet types' for_ attributes")
