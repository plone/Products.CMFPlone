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
if REQUEST.has_key('ids'):
    transaction_note( str(REQUEST['ids'])+' has been deleted' )
    context.manage_delObjects(REQUEST['ids'], REQUEST)
    return context.portal_navigation.getNextRequestFor( context
                                                , script.getId()
                                                , 'success'
                                                , portal_status_message='Deleted.' )

return context.portal_navigation.getNextRequestFor( context
                                            , script.getId()
                                            , 'failure'
                                            , portal_status_message='Please select one or more items to delete.' )
