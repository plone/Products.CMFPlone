## Controller Python Script "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##

from Products.CMFPlone import transaction_note
ids=context.REQUEST.get('ids', None)
titles=[]

status='failure'
message='Please select one or more items to delete.'

for id in ids:
    obj=context.restrictedTraverse(id)
    titles.append(obj.title_or_id())

if ids:
    status='success'
    message=', '.join(titles)+' has been deleted.'
    transaction_note(message)
    context.manage_delObjects(ids)
    from Products.CMFPlone import transaction_note
    transaction_note('Deleted %s from %s' % (str(REQUEST['ids']), context.absolute_url()))

return state.set(status=status, portal_status_message=message)

