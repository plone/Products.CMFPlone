## Script (Python) "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.CMFPlone import transaction_note
ids=context.REQUEST.get('ids', None)

# Get homefolder of user

homeFolder = context.portal_membership.getHomeFolder()

# Create Trashcan if it not exists

if '.trashcan' not in homeFolder.objectIds():
    homeFolder.invokeFactory(id='.trashcan', title='Trashcan', type_name='Folder')
    homeFolder.folder_publish(workflow_action='hide', ids=['.trashcan'])

# Get Trashcan

status='failure'
status_msg='Please select one or more items to delete.'

if ids:
    Trashcan = getattr(homeFolder.aq_explicit, '.trashcan')
    
    # If current Folder is Trashcan, then delete objects.

    if context == Trashcan:
        status='success'
        message=', '.join(ids)+' has been deleted.'
        transaction_note(message)        
        Trashcan.manage_delObjects(ids)

    # If not, move objects to Trashcan

    else:
        status='success'
        message=', '.join(ids)+' has been moved to Trashcan.'
        transaction_note(message)
        
        # First we have to retract all objects...
        
        context.folder_publish(workflow_action='retract', ids=ids, include_subfolders=1)
        
        # ... then hide them => All objects will be private after that operations.
        
        context.folder_publish(workflow_action='hide', ids=ids, include_subfolders=1)
        
        cp=context.manage_cutObjects(ids)
        Trashcan.manage_pasteObjects(cb_copy_data=cp)

return context.portal_navigation.getNext(
                      context,
                      script.getId(),
                      status,
                      portal_status_message=message)
