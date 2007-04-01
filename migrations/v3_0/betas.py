from zope.component import queryUtility

from Products.CMFCore.interfaces import IActionsTool, ITypesTool
from Products.CMFCore.Expression import Expression
from Products.ResourceRegistries.interfaces import IJSRegistry

def beta1_beta2(portal):
    """ 3.0-beta1 -> 3.0-beta2
    """

    out = []

    migrateHistoryTab(portal, out)
    changeOrderOfActionProviders(portal, out)
    updateEditActionConditionForLocking(portal, out)
    addOnFormUnloadJS(portal, out)

    return out


def migrateHistoryTab(portal, out):
    portal_actions = queryUtility(IActionsTool)
    if portal_actions is not None:
        objects = getattr(portal_actions, 'object', None)
        if objects is not None:
            if 'rss' in objects.objectIds():
                objects.manage_renameObjects(['rss'], ['history'])
                out.append('Migrated history action.')

def changeOrderOfActionProviders(portal, out):
    portal_actions = queryUtility(IActionsTool)
    if portal_actions is not None:
        portal_actions.deleteActionProvider('portal_actions')
        portal_actions.addActionProvider('portal_actions')
        out.append('Changed the order of action providers.')

def updateEditActionConditionForLocking(portal, out):
    """
    Condition on edit views for Document, Event, File, Folder, Image, 
    Large_Plone_Folder, Link, Topic has been added to not display the Edit
    tab if an item is locked
    """
    portal_types = queryUtility(ITypesTool)
    lockable_types = ['Document', 'Event', 'Favorite', 'File', 'Folder',
                      'Image', 'Large Plone Folder', 'Link',
                      'News Item', 'Topic']
    if portal_types is not None:
        for contentType in lockable_types:
            fti = portal_types.getTypeInfo(contentType)
            if fti:
                for action in fti.listActions():
                    if action.getId() == 'edit' and not action.condition:
                        action.condition = Expression("not:object/@@plone_lock_info/is_locked_for_current_user|python:True")

def addOnFormUnloadJS(portal, out):
    """
    add the form unload JS to the js registry
    """
    jsreg = queryUtility(IJSRegistry)
    script = 'unlockOnFormUnload.js'
    if jsreg is not None:
        script_ids = jsreg.getResourceIds()
        # Failsafe: first make sure the stylesheet doesn't exist in the list
        if script not in script_ids:
            jsreg.registerScript(script,
                                 enabled = True,
                                 cookable = True)
            # put it at the bottom of the stack
            jsreg.moveResourceToBottom(script)
            out.append("Added " + script + " to portal_javascipt")

