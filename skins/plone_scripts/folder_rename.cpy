## Controller Python Script "folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=new_ids=[],old_ids=[],new_titles=[]
##title=Rename Objects
##
from Products.CMFPlone import transaction_note

for x in range(0, len(new_ids):
    old_id = old_ids[x]
    new_title = new_titles[x]
    obj = context.restrictedTraverse(old_id)
    if o.Title() != new_title:
        o.setTitle(new_title)

context.manage_renameObjects(old_ids, new_ids)
transaction_note( str(old_ids) + 'have been renamed' )

return state.set(portal_status_message='Item(s) renamed.')
