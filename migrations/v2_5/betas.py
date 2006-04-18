import os
from Acquisition import aq_base

from Products.GenericSetup.tool import SetupTool

from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.CMFPlone.migrations.v2_1.alphas import reindexCatalog, indexMembersFolder
from Products.CMFPlone.migrations.v2_1.two12_two13 import normalizeNavtreeProperties
from Products.CMFPlone.migrations.v2_1.two12_two13 import removeVcXMLRPC
from Products.CMFPlone.migrations.v2_1.two12_two13 import addActionDropDownMenuIcons
from Products.CMFPlone.migrations.v2_5.alphas import installDeprecated
from Products.CMFPlone.factory import _TOOL_ID as SETUP_TOOL_ID

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import createDirectoryView
from Products.CMFCore.Expression import Expression

def alpha2_beta1(portal):
    """2.5-alpha2 -> 2.5-beta1
    """
    out = []

    # Add dragdropreorder.js to ResourceRegistries.
    addDragDropReorderJS(portal, out)

    # Add getEventTypes KeywordIndex to portal_catalog
    addGetEventTypeIndex(portal, out)

    # Fix 'home' portal action
    fixHomeAction(portal, out)

    # Fixup the navtree properties (this was already done in 2.1.3, but may
    # need to be done again for those migrating from alphas)
    normalizeNavtreeProperties(portal, out)


    return out

def beta1_beta2(portal):
    """2.5-beta1 - > 2.5-beta2
    """
    out = []

    # The migration done during the alpha screwed things up, so we do it again
    # and fix the mistake while we're at it
    installDeprecated(portal, out)
    removeBogusSkin(portal, out)

    # add a property indicating if this is a big or small site, so the UI can
    # change depending on it
    propTool = getToolByName(portal, 'portal_properties', None)
    propSheet = getattr(propTool, 'site_properties', None)
    if not propSheet.hasProperty('large_site'):
        propSheet.manage_addProperty('large_site', 0, 'boolean')
        out.append("Added 'large_site' property to site_properties.")

    # Remove vcXMLRPC.js from ResourceRegistries (this was already done in
    # 2.1.3, but may need to be done again for those migrating from alphas)
    removeVcXMLRPC(portal, out)

    # Required due to a fix in PortalTransforms...
    reindexCatalog(portal, out)

    # FIXME: *Must* be called after reindexCatalog.
    # In tests, reindexing loses the folders for some reason...

    # Make sure the Members folder is cataloged
    indexMembersFolder(portal, out)

    # add icons for copy, cut, paste and delete
    addActionDropDownMenuIcons(portal, out)

    # add any appropriate plone skin layers to custom skins
    addPloneSkinLayers(portal, out)

    # Install portal_setup
    installPortalSetup(portal, out)

    return out

def addDragDropReorderJS(portal, out):
    """Add dragdropreorder.js to ResourceRegistries.
    """
    jsreg = getToolByName(portal, 'portal_javascripts', None)
    script = 'dragdropreorder.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script)
            try:
                jsreg.moveResourceAfter(script, 'dropdown.js')
            except ValueError:
                # put it at the bottom of the stack
                jsreg.moveResourceToBottom(script)
            out.append("Added " + script + " to portal_javascipt")

def addGetEventTypeIndex(portal, out):
    """Adds the getEventType KeywordIndex."""
    catalog = getToolByName(portal, 'portal_catalog', None)
    if catalog is not None:
        try:
            index = catalog._catalog.getIndex('getEventType')
        except KeyError:
            pass
        else:
            indextype = index.__class__.__name__
            if indextype == 'KeywordIndex':
                return 0
            catalog.delIndex('getEventType')
            out.append("Deleted %s 'getEventType' from portal_catalog." % indextype)

        catalog.addIndex('getEventType', 'KeywordIndex')
        out.append("Added KeywordIndex 'getEventType' to portal_catalog.")
        return 1 # Ask for reindexing
    return 0

def fixHomeAction(portal, out):
    """Make the 'home' action use the @@plone view to get a properly rooted
    navtree.
    """
    newaction = { 'id'         : 'index_html',
                  'name'       : 'Home',
                  'action'     : 'string:${here/@@plone/navigationRootUrl}',
                  'condition'  : '',
                  'permission' : 'View',
                  'category'   : 'portal_tabs',
                }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == newaction['id'] and action.category == newaction['category']:
                exists = True
                action.condition = Expression(text=newaction['condition']) or ''
                out.append('Modified existing home/index_html action')
        if exists:
            actionsTool._actions = new_actions
        else:
            actionsTool.addAction(newaction['id'],
                    name=newaction['name'],
                    action=newaction['action'],
                    condition=newaction['condition'],
                    permission=newaction['permission'],
                    category=newaction['category'],
                    visible=1)
            out.append("Added missing home/index_html action")

def removeBogusSkin(portal, out):
    skins = getToolByName(portal, 'portal_skins', None)
    if skins is not None:
        if skins._getSelections().has_key('cmf_legacy'):
            skins.manage_skinLayers(('cmf_legacy',), del_skin=True)
            out.append("Deleted incorrectly added 'cmf_legacy' skin")

def addPloneSkinLayers(portal, out):
    st = getToolByName(portal, 'portal_skins', None)
    if st is None:
        out.append('No portal_skins tool')
        return
    
    for skin in st._getSelections().keys():
        path = st.getSkinPath(skin)
        path = [p.strip() for p in path.split(',')]
        if not 'plone_deprecated' in path:
            path.append('plone_deprecated')
            st.addSkinSelection(skin, ','.join(path))
            out.append('Added plone_deprecated to %s' % skin)

def installPortalSetup(portal, out):
    """Adds portal_setup if not installed yet."""
    if SETUP_TOOL_ID not in portal.objectIds():
        portal._setObject(SETUP_TOOL_ID, SetupTool(SETUP_TOOL_ID))
        out.append('Added setup_tool.')
