## Script (Python) "folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Rename Object
##
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST
x=0
new_ids=REQUEST['new_ids']
old_ids=REQUEST['ids']
new_titles=REQUEST['new_titles']

for id in new_ids:
    old_id=old_ids[x]
    new_title=new_titles[x]
    o=getattr(context,old_id)
    if o.Title()!=new_title:
        o.setTitle(new_title)
    x=x+1
    
if not new_ids:
    return context.portal_navigation.getNextRequestFor( context
                                                , script.getId()
                                                , 'failure'
                                                , portal_status_message='No Item(s) Marked For Renaming' )
                                                
context.manage_renameObjects(REQUEST['ids'], REQUEST['new_ids'], REQUEST)
transaction_note( str(REQUEST['ids']) + 'have been renamed' )

return context.portal_navigation.getNextRequestFor( context
                                            , script.getId()
                                            , 'success'
                                            , portal_status_message='Item(s) Renamed' )
