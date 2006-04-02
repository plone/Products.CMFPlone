import os
from Acquisition import aq_base

from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
from Products.CMFPlone.migrations.v2_1.two12_two13 import normalizeNavtreeProperties
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

    # Fixup the navtree properties (this was already done in 1.3, but may
    # need to be done again for those migrating from alphas)
    normalizeNavtreeProperties(portal, out)


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
