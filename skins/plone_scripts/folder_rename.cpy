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
    id = ids[x]
    new_title = new_titles[x]
    obj = context.restrictedTraverse(id)
    if obj.Title() != new_title:
        obj.setTitle(new_title)

context.manage_renameObjects(ids, new_ids)
transaction_note( str(ids) + 'have been renamed' )

return state.set(portal_status_message='Item(s) renamed.')
