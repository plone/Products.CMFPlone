## Controller Python Script "folder_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects into a folder
##

REQUEST=context.REQUEST
msg='Copy or cut one or more items to paste.' 

if context.cb_dataValid:
    try:
        context.manage_pasteObjects(REQUEST['__cp'])
        return state.set(portal_status_message='Item(s) pasted.')
    except:
        msg='Paste could not find clipboard content'

return state.set(status='failure', portal_status_message=msg)

