## Controller Python Script "folder_copy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Copy object from a folder to the clipboard
##
REQUEST=context.REQUEST
if REQUEST.has_key('paths'):
    ids = [p.split('/')[-1] or p.split('/')[-2] for p in REQUEST['paths']]
    context.manage_copyObjects(ids, REQUEST, REQUEST.RESPONSE)

    from Products.CMFPlone import transaction_note
    transaction_note('Copied %s from %s' % (str(ids), context.absolute_url()))

    return state.set(portal_status_message='%s Item(s) copied.'%len(ids))

return state.set(status='failure', portal_status_message='Please select one or more items to copy.')
