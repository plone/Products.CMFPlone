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
ids=context.REQUEST.get('ids', [])
titles=[]
titles_and_ids=[]

status='failure'
message='Please select one or more items to delete.'

for id in ids:
    obj=context.restrictedTraverse(id)
    titles.append(obj.title_or_id())
    titles_and_ids.append('%s (%s)' % (obj.title_or_id(), obj.getId()))

if ids:
    status='success'
    if len(titles) == 1:
        message = context.translate("${title} has been deleted.",
                                    {'title': titles[0]})
    else:
        message = context.translate("${titles} have been deleted.",
                                    {'titles': ', '.join(titles)})

    transaction_note('Deleted %s from %s' % (', '.join(titles_and_ids), context.absolute_url()))
    context.manage_delObjects(ids)

return state.set(status=status, portal_status_message=message)

