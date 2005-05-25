from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression


def alpha2_beta1(portal):
    """2.1-alpha2 -> 2.1-beta1
    """
    out = []

    #Make object paste action work with all default pages.
    fixObjectPasteActionForDefaultPages(portal, out)

    # Fix folderlisting action for folders
    fixFolderlistingAction(portal, out)

    return out


def fixObjectPasteActionForDefaultPages(portal, out):
    """ Change the plone_setup action so that its title is Site Setup.
    """
    newaction =  {'id'        : 'paste',
                  'name'      : 'Paste',
                  'action'    : 'python:"%s/object_paste"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)',
                  'condition' : 'folder/cb_dataValid',
                  'permission': CMFCorePermissions.View,
                  'category': 'object_buttons',
                 }
    exists = False
    actionsTool = getToolByName(portal, 'portal_actions', None)
    if actionsTool is not None:
        new_actions = actionsTool._cloneActions()
        for action in new_actions:
            if action.getId() == newaction['id'] and action.category == newaction['category']:
                exists = True
                action.setActionExpression(Expression(newaction['action']))
                out.append('Modified existing object paste action for folderish default pages')
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
            out.append("Added missing object paste action")
            
def fixFolderlistingAction(portal, out):
    typesTool = getToolByName(portal, 'portal_types', None)
    if typesTool is not None:
        folderFTI = getattr(typesTool, 'Folder', None)
        if folderFTI is not None:
            haveFolderListing = False
            for action in folderFTI.listActions():
                if action.getId() == 'folderlisting':
                    action.setActionExpression('view')
                    haveFolderListing = True
                    break
            if not haveFolderListing:
                folderFTI.addAction('folderlisting',
                                    'Folder view',
                                    'string:${folder_url}/view',
                                    '',
                                    'View',
                                    'folder',
                                    visible=0)
            out.append("Set target expresion of folderlisting action for 'Folder' to 'view'")
        siteFTI = getattr(typesTool, 'Plone Site', None)
        if siteFTI is not None:
            haveFolderListing = False
            for action in siteFTI.listActions():
                if action.getId() == 'folderlisting':
                    action.setActionExpression('view')
                    haveFolderListing = True
                    break
            if not haveFolderListing:
                siteFTI.addAction('folderlisting',
                                    'Folder view',
                                    'string:${folder_url}/view',
                                    '',
                                    'View',
                                    'folder',
                                    visible=0)
            out.append("Set target expresion of folderlisting action for 'Plone Site' to 'view'")