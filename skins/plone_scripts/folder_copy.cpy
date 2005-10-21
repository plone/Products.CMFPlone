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
from Products.CMFPlone import transaction_note
from Products.CMFPlone import PloneMessageFactory as _

REQUEST=context.REQUEST
if REQUEST.has_key('paths'):
    ids = [p.split('/')[-1] or p.split('/')[-2] for p in REQUEST['paths']]
    
    try:
        context.manage_copyObjects(ids, REQUEST, REQUEST.RESPONSE)
    except CopyError:
        message = _(u'One or more items not copyable.')
        return state.set(status = 'failure', portal_status_message = message)
    except AttributeError:
        message = _(u'One or more selected items is no longer available.')
        return state.set(status = 'failure', portal_status_message = message)

    transaction_note('Copied %s from %s' % (str(ids), context.absolute_url()))

    message = _(u'${count} item(s) copied.')
    message.mapping[u'count'] = len(ids)

    return state.set(portal_status_message=message)

return state.set(status='failure', portal_status_message=_(u'Please select one or more items to copy.'))
