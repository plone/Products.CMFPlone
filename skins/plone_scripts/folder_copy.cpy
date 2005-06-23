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
from OFS.CopySupport import CopyError

REQUEST=context.REQUEST
if REQUEST.has_key('paths'):
    ids = [p.split('/')[-1] or p.split('/')[-2] for p in REQUEST['paths']]
    
    try:
        context.manage_copyObjects(ids, REQUEST, REQUEST.RESPONSE)
    except CopyError:
        message = context.translate("One or more items not copyable.")
        context.plone_utils.addPortalMessage(message)
        return state.set(status = 'failure')
    except AttributeError:
        message = context.translate("One or more selected items is no longer available.")
        context.plone_utils.addPortalMessage(message)
        return state.set(status = 'failure')

    from Products.CMFPlone import transaction_note
    transaction_note('Copied %s from %s' % (str(ids), context.absolute_url()))

    context.plone_utils.addPortalMessage('%s Item(s) copied.' % len(ids))
    return state

context.plone_utils.addPortalMessage('Please select one or more items to copy.')
return state.set(status='failure')
