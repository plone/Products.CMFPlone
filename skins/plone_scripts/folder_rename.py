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
new_ids=REQUEST['new_ids']
old_ids=REQUEST['ids']
new_titles=REQUEST['new_titles']

x=0
for id in new_ids:
    old_id=old_ids[x]
    new_title=new_titles[x]
    o=getattr(context,old_id)
    if o.Title()!=new_title:
        o.setTitle(new_title)
    x=x+1

context.manage_renameObjects(old_ids, new_ids) #x, REQUEST)
transaction_note( str(old_ids) + 'have been renamed' )

return ( 'success', 
         context, 
         {'portal_status_message':'Item(s) renamed.'} )

