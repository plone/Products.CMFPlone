## Script (Python) "folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Rename Object
##
REQUEST=context.REQUEST
changed=0
for id in REQUEST['new_ids']:
    if id:
        changed=1
if not changed: 
    return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=No+Item(s)+Marked+For+Renaming.')


context.manage_renameObjects(REQUEST['ids'], REQUEST['new_ids'], REQUEST)
return REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_contents?portal_status_message=Item(s)+Renamed.')
