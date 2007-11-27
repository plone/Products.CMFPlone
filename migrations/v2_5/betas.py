import re
from Acquisition import aq_base

from Products.GenericSetup.tool import SetupTool

from Products.CMFPlone.migrations.v2_1.two12_two13 import normalizeNavtreeProperties
from Products.CMFPlone.migrations.v2_1.two12_two13 import removeVcXMLRPC
from Products.CMFPlone.migrations.v2_1.two12_two13 import addActionDropDownMenuIcons
from Products.CMFPlone.migrations.v2_5.alphas import installDeprecated
from Products.CMFPlone.factory import _TOOL_ID as SETUP_TOOL_ID

from Products.CMFCore.utils import getToolByName
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

    # add icons for copy, cut, paste and delete
    addActionDropDownMenuIcons(portal, out)

    # add any appropriate plone skin layers to custom skins
    addPloneSkinLayers(portal, out)

    # Install portal_setup
    installPortalSetup(portal, out)

    # Simplify actions using the @@plone view
    simplifyActions(portal, out)

    # Use the @@plone view for the RTL.css expression entry
    migrateCSSRegExpression(portal, out)

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
        if 'getEventType' in catalog.indexes():
            index = [i for i in catalog.index_objects() if
                                         i.getId() == 'getEventType']
            indextype = index.__class__.__name__
            if indextype == 'KeywordIndex':
                return 0
            catalog.delIndex('getEventType')
            out.append("Deleted %s 'getEventType' from portal_catalog." %
                       indextype)

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

# A set of regexes and substitution strings for cleaning up the current
# actions, in particular to make optimal use of the methods provided by
# @@plone and remove deprecation warnings.
action_replacements = [
# Remove leading space from string and python expressions, it is annoying
(re.compile(r"^string: "),
 r"string:"),
(re.compile(r"^python: "),
 r"python:"),
(re.compile(r"portal\.portal_membership\.checkPermission"),
 r"checkPermission"),
(re.compile(r"^python:\(\(object\.isDefaultPageInFolder\(\) and object.getParentNode\(\)\.absolute_url\(\)\) or folder_url\)\+(?:\"|')/(.+)(?:\"|')$"),
 r"string:${globals_view/getCurrentFolderUrl}/\1"),
(re.compile(r"python:(?:\"|')%s/(.+)(?:\"|')%\(\(object\.isDefaultPageInFolder\(\) or not object\.is_folderish\(\)\) and object\.getParentNode\(\)\.absolute_url\(\) or object_url\)$"),
 r"string:${globals_view/getCurrentFolderUrl}/\1"),
(re.compile(r"^python:(?:\"|')%s/(.+)(?:\"|')%\(object\.isDefaultPageInFolder\(\) and object.getParentNode\(\)\.absolute_url\(\) or object_url\)$"),
 r"string:${globals_view/getCurrentObjectUrl}/\1"),
(re.compile(r"object is not portal and not \(object\.isDefaultPageInFolder\(\) and object\.getParentNode\(\) is portal\)"),
 r"not globals_view.isPortalOrPortalDefaultPage()"),
(re.compile(r"object\.aq_inner\.getParentNode\(\)"),
 r"globals_view.getParentObject()"),
(re.compile("here/@@plone"),
 r"globals_view"),
(re.compile(r"^python:portal\.portal_membership\.getHomeUrl\(\)\+(?:\"|')/(.+)(?:\"|')$"),
 r"string:${portal/portal_membership/getHomeUrl}/\1"),
]

def simplifyActions(portal, out):
    from Products.CMFCore.ActionInformation import ActionInformation
    action_tool = getToolByName(portal, 'portal_actions', None)
    if action_tool is not None:
        providers = action_tool.listActionProviders()
        # Iterate ofer all action providers
        for provider in providers:
            tool = getToolByName(portal, provider, None)
            # If this is not a provider with persistent Action objects skip it
            if not getattr(tool, '_actions', None) or \
               not isinstance(tool._actions[0], ActionInformation):
                continue
            actions = tool.listActions()
            # iterate through the actions and for each action check if it
            # matches any of the patterns we want to replace
            for action in actions:
                action_id = '%s/%s/%s'%(provider, action.getCategory(),
                                        action.getId())
                cur_expr = action.getActionExpression()
                cur_condition = action.getCondition()
                for regex, replacement in action_replacements:
                    new_expr = regex.sub(replacement, cur_expr)
                    new_condition = regex.sub(replacement, cur_condition)
                    if new_expr != cur_expr:
                        action.setActionExpression(new_expr)
                        out.append(
                      'Changed url expression on action %s from: \n%s\nto:\n%s'%(
                                             action_id, cur_expr, new_expr))
                    if new_condition != cur_condition:
                        action.edit(condition=new_condition)
                        out.append(
                           'Changed condition on action %s from: \n"%s"\nto:\n"%s"'%(
                                         action_id, cur_condition, new_condition))
                    cur_expr = new_expr
                    cur_condition = new_condition


def migrateCSSRegExpression(portal, out):
    """Changes calls to the isRightToLeft script to use the view, also
       replaces the use of restrictedTraverse with a more compact path
       expression."""
    css_reg = getToolByName(portal, 'portal_css', None)
    if css_reg is not None:
        resource = css_reg.getResource('RTL.css')
        # The None that comes out of RR is apparently acquisition wrapped,
        # nasty.
        if aq_base(resource) is not None:
            css_expr = resource.getExpression()
            new_expr = 'object/@@plone/isRightToLeft'
            if "object.isRightToLeft" in css_expr or \
               "object.restrictedTraverse('@@plone')" in css_expr:
                resource.setExpression(new_expr)
                css_reg.cookResources()
                out.append("Fixed RTL.css expression to use the @@plone view")
