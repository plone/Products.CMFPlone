from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site
from Products.CMFPlone.migrations.v3_0.alphas import registerToolsAsUtilities


def beta2_rc1(portal):
    """2.5-beta2 -> 2.5-rc1
    """
    out = []

    # Make the portal a Zope3 site
    enableZope3Site(portal, out)

    # register some tools as utilities
    registerToolsAsUtilities(portal, out)

    # add a property indicating if this is a big or small site, so the UI can
    # change depending on it
    propTool = getToolByName(portal, 'portal_properties', None)
    propSheet = getattr(propTool, 'site_properties', None)
    if not propSheet.hasProperty('many_users'):
        if propSheet.hasProperty('large_site'):
            out.append("Migrating 'large_site' to 'many_users' property.")
            default=propSheet.getProperty('large_site')
            propSheet.manage_delProperties(ids=['large_site'])
        else:
            default=0
        propSheet.manage_addProperty('many_users', default, 'boolean')
        out.append("Added 'many_users' property to site_properties.")

