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
new_ids=REQUEST.get('new_ids',None)
old_ids=REQUEST.get('ids',None)
new_titles=REQUEST.get('new_titles',None)

x=0
for id in new_ids:
    old_id=old_ids[x]
    new_title=new_titles[x]
    o=getattr(context,old_id)
    if o.Title()!=new_title:
        o.setTitle(new_title)
    x=x+1

context.manage_renameObjects(REQUEST['ids'], REQUEST['new_ids'], REQUEST)
transaction_note( str(REQUEST['ids']) + 'have been renamed' )

return ('success', context, {'portal_status_message':'Item(s) renamed'})
