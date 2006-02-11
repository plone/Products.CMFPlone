import os
import string
from Acquisition import aq_base

from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import createDirectoryView

def two5_alpha1(portal):
    """2.1.2 -> 2.5-alpha1
    """
    out = []

    # Install CMFPlacefulWorkflow
    installPlacefulWorkflow(portal, out)

    return out

def alpha1_alpha2(portal):
    """2.1.2 -> 2.5-alpha1
    """
    out = []

    # Install plone_deprecated skin
    installDeprecated(portal, out)

    return out


def installPlacefulWorkflow(portal, out):
    """Quickinstalls CMFPlacefulWorkflow if not installed yet."""
    # CMFPlacefulWorkflow is not installed by e.g. tests
    if 'CMFPlacefulWorkflow' in portal.Control_Panel.Products.objectIds():
        installOrReinstallProduct(portal, 'CMFPlacefulWorkflow', out)

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
        path = [s.strip() for s in  path.split(',')]
        if not 'plone_deprecated' in path:
            if 'plone_3rdparty' in path:
                path.insert(path.index('plone_3rdparty'), 'plone_login')
            else:
                path.append('plone_deprecated')
            st.addSkinSelection(s, ','.join(path))
            out.append('Added plone_deprecated to %s' % s)
