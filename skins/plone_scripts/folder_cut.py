## Script (Python) "folder_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cut objects from a folder and copy to the clipboard
##
REQUEST=context.REQUEST
if REQUEST.has_key('ids'):
    context.manage_cutObjects(REQUEST['ids'], REQUEST)
    return context.portal_navigation.getNext( context
                , script.getId()
                , 'success'
                , portal_status_message='Item(s) cut.' )
                                                
return context.portal_navigation.getNext( context
            , script.getId()
            , 'failure'
            , portal_status_message='Please select one or more items to cut.' )
