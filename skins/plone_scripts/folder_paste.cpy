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

msg='Copy or cut one or more items to paste.' 

if context.cb_dataValid:
    try:
        context.manage_pasteObjects(context.REQUEST['__cp'])
        from Products.CMFPlone import transaction_note
        transaction_note('Pasted content to %s' % (context.absolute_url()))
        return state.set(portal_status_message='Item(s) pasted.')
    except ValueError: 
        msg="Disallowed to paste item(s)."
    except 'Unauthorized':
        msg="Unauthorized to paste item(s)."
    except: # fallback
        msg='Paste could not find clipboard content.'

return state.set(status='failure', portal_status_message=msg)

