## Controller Python Script "folder_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Cut objects from a folder and copy to the clipboard
##

REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
    context.manage_cutObjects(REQUEST['ids'], REQUEST)

    from Products.CMFPlone import transaction_note
    transaction_note('Cut %s from %s' % (str(REQUEST['ids']), context.absolute_url()))

    return state.set(portal_status_message='Item(s) cut.' )
                                                
return state.set(status='failure', portal_status_message='Please select one or more items to cut.')