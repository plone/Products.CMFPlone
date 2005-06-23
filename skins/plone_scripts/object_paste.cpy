## Controller Python Script "object_paste"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Paste objects into the parent/this folder
##

from Products.CMFPlone import transaction_note
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError

msg='Copy or cut one or more items to paste.' 

if context.cb_dataValid:
    try:
        context.manage_pasteObjects(context.REQUEST['__cp'])        
        transaction_note('Pasted content to %s' % (context.absolute_url()))
        context.plone_utils.addPortalMessage('Item(s) pasted.')
        return state
    except ConflictError:
        raise
    except ValueError: 
        msg="Disallowed to paste item(s)."
    except (Unauthorized, 'Unauthorized'):
        msg="Unauthorized to paste item(s)."
    except: # fallback
        msg='Paste could not find clipboard content.'

context.plone_utils.addPortalMessage(msg)
return state.set(status='failure')
