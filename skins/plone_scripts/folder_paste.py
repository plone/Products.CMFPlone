## Script (Python) "folder_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects to a folder from the clipboard
##
REQUEST=context.REQUEST

if context.cb_dataValid:
    context.manage_pasteObjects(REQUEST['__cp'])
    return context.portal_navigation.getNext( context
                , script.getId()
                , 'success'
                , portal_status_message='Item(s) pasted.' ) 

return context.portal_navigation.getNext( context
            , script.getId()
            , 'failure'
            , portal_status_message='Copy or cut one or more items to paste.' )
