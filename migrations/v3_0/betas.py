from zope.component import queryUtility

from Products.CMFCore.interfaces import IActionsTool, ITypesTool
from Products.CMFCore.Expression import Expression
#from Products.CMFCore.ActionInformation import Action
#from Products.CMFCore.ActionInformation import ActionInformation

def beta1_beta2(portal):
    """ 3.0-beta1 -> 3.0-beta2
    """

    out = []

    migrateHistoryTab(portal, out)
    changeOrderOfActionProviders(portal, out)
    updateEditActionConditionForLocking(portal, out)

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
