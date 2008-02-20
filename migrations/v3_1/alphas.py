from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.migrations.migration_util import loadMigrationProfile

def three0_alpha1(portal):
    """3.0.6 -> 3.1alpha1
    """
    out = []

    loadMigrationProfile(portal, 'profile-Products.CMFPlone:plone')
    addBrowserLayer(portal, out)

    return out


def addBrowserLayer(portal, out):
    qi=getToolByName(portal, "portal_quickinstaller")
    if not qi.isProductInstalled("plone.browserlayer"):
        qi.installProduct("plone.browserlayer", locked=True)
        out.append("Installed plone.browserlayer")
