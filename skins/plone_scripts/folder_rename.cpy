## Controller Python Script "folder_rename"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[],new_ids=[],new_titles=[]
##title=Rename Objects
##

from Products.CMFPlone import transaction_note

for x in range(0, len(new_ids)):
    new_id = new_ids[x]
    id = ids[x]
    new_title = new_titles[x]
    obj = context.restrictedTraverse(id)
    if new_title and obj.Title() != new_title:
        obj.setTitle(new_title)
    if new_id and id != new_id:
        context.manage_renameObjects((id,), (new_id,))

transaction_note( str(ids) + 'have been renamed' )
return state.set(portal_status_message='Item(s) renamed.')
