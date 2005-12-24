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
from ZODB.POSException import ConflictError

plone_utils = getToolByName(context, 'plone_utils')
mtool = getToolByName(context, 'portal_membership')
site_properties = getToolByName(context, 'portal_properties').site_properties
pretty_title_or_id = plone_utils.pretty_title_or_id
empty_title = plone_utils.getEmptyTitle()

if not mtool.checkPermission(AllowSendto, context):
    return state.set(
            status='failure',
            portal_status_message='You are not allowed to send this link.')

at = getToolByName(context, 'portal_actions')
show = False
actions = at.listActionInfos(object=context)
# Check for visbility of sendto action
for action in actions:
    if action['id'] == 'sendto' and action['category'] == 'document_actions':
        show = True
if not show:
    return state.set(
        status='failure',
        portal_status_message='You are not allowed to send this link.')

# Try to find the view action. If not found, use absolute_url()
url = context.absolute_url()
ti = context.getTypeInfo()
if ti is not None:
    view = ti.getActionById('view', '')
    if view:
        url = '/'.join((url, view))

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
    message = context.translate("Unable to send mail: ${exception}",
                                {'exception': exception})
    return state.set(status='failure', portal_status_message=message)

tmsg='Sent page %s to %s' % (url, REQUEST.send_to_address)
transaction_note(tmsg)

return state.set(portal_status_message='Mail sent.')
