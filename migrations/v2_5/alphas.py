import os
from Acquisition import aq_base

from Products.GenericSetup.tool import SetupTool

from Products.CMFPlone.factory import _TOOL_ID as SETUP_TOOL_ID
from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import createDirectoryView

def two5_alpha1(portal):
    """2.1.2 -> 2.5-alpha1
    """
    out = []

    # Install CMFPlacefulWorkflow
    installPlacefulWorkflow(portal, out)

    # Install portal_setup
    installPortalSetup(portal, out)
    
    return out

def alpha1_alpha2(portal):
    """2.5-alpha1 -> 2.5-alpha2
    """
    out = []

    # Install PlonePAS
    installPlonePAS(portal, out)

    # Install plone_deprecated skin
    installDeprecated(portal, out)

    return out


def installPlacefulWorkflow(portal, out):
    """Quickinstalls CMFPlacefulWorkflow if not installed yet."""
    # CMFPlacefulWorkflow is not installed by e.g. tests
    if 'CMFPlacefulWorkflow' in portal.Control_Panel.Products.objectIds():
        installOrReinstallProduct(portal, 'CMFPlacefulWorkflow', out)

def installPlonePAS(portal, out):
    """Quickinstalls PlonePAS if not installed yet."""
    installOrReinstallProduct(portal, 'PasswordResetTool', out)
    installOrReinstallProduct(portal, 'PlonePAS', out)

def installPortalSetup(portal, out):
    """Adds portal_setup if not installed yet."""
    if SETUP_TOOL_ID not in portal.objectIds():
        portal._setObject(SETUP_TOOL_ID, SetupTool(SETUP_TOOL_ID))
        out.append('Added setup_tool.')

def installDeprecated(portal, out):
    # register login skin
    st = getToolByName(portal, 'portal_skins', None)
    if st is None:
        return
    if not hasattr(aq_base(st), 'plone_deprecated'):
        createDirectoryView(st, os.path.join('CMFPlone', 'skins', 'plone_deprecated'))
        out.append('Added directory view for plone_deprecated')

    # add deprecated skin to default skins
    skins = ['Plone Default', 'Plone Tableless']
    selections = st._getSelections()
    for s in skins:
        if not selections.has_key(s):
           continue
        path = st.getSkinPath(s)
        path = [p.strip() for p in  path.split(',')]
        if not 'plone_deprecated' in path:
            if 'plone_3rdParty' in path:
                path.insert(path.index('plone_3rdParty'), 'plone_deprecated')
            else:
                path.append('plone_deprecated')
            st.addSkinSelection(s, ','.join(path))
            out.append('Added plone_deprecated to %s' % s)

