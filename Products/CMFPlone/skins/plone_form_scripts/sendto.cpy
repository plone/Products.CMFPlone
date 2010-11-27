## Controller Python Script "sendto"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send an URL to a friend
##
REQUEST=context.REQUEST

from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone.PloneTool import AllowSendto
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from ZODB.POSException import ConflictError

plone_utils = getToolByName(context, 'plone_utils')
mtool = getToolByName(context, 'portal_membership')
site_properties = getToolByName(context, 'portal_properties').site_properties
pretty_title_or_id = plone_utils.pretty_title_or_id

if not mtool.checkPermission(AllowSendto, context):
    context.plone_utils.addPortalMessage(_(u'You are not allowed to send this link.'), 'error')
    return state.set(status='failure')

# Find the view action.
context_state = context.restrictedTraverse("@@plone_context_state")
url = context_state.view_url()

variables = {'send_from_address' : REQUEST.send_from_address,
             'send_to_address'   : REQUEST.send_to_address,
             'subject'           : pretty_title_or_id(context),
             'url'               : url,
             'title'             : pretty_title_or_id(context),
             'description'       : context.Description(),
             'comment'           : REQUEST.get('comment', None),
             'envelope_from'     : site_properties.email_from_address
             }

try:
    plone_utils.sendto( **variables )
except ConflictError:
    raise
except: # TODO To many things could possibly go wrong. So we catch all.
    exception = context.plone_utils.exceptionString()
    message = _(u'Unable to send mail: ${exception}',
                mapping={u'exception' : exception})
    context.plone_utils.addPortalMessage(message, 'error')
    return state.set(status='failure')

tmsg='Sent page %s to %s' % (url, REQUEST.send_to_address)
transaction_note(tmsg)

context.plone_utils.addPortalMessage(_(u'Mail sent.'))
return state
