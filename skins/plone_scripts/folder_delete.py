## Script (Python) "folder_delete"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Delete objects from a folder
##
from Products.CMFPlone import transaction_note
REQUEST=context.REQUEST
portal_navigation=context.portal_navigation

ids=REQUEST.get('ids', None)
status='failure'
status_msg='Please select one or more items to delete.'

if ids:
    transaction_note( str(ids)+' has been deleted' )
    context.manage_delObjects(ids, REQUEST)
    status='success'
    status_msg='Deleted.'

return portal_navigation.getNext( context
                                , script.getId()
                                , status
                                , portal_status_message=status_msg )
