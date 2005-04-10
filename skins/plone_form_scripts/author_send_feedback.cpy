## Controller Python Script "author_send_feedback"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send feedback to an author
##
REQUEST=context.REQUEST

from Products.CMFPlone import transaction_note
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

plone_utils = getToolByName(context, 'plone_utils')
mtool = getToolByName(context, 'portal_membership')

site_properties = getToolByName(context, 'portal_properties').site_properties

## make these arguments?
referer = REQUEST.get('referer', 'unknown referer')
subject = REQUEST.get('subject', '')
message = REQUEST.get('message', '')
author = REQUEST.get('author')

sender = mtool.getAuthenticatedMember()

send_to_address = mtool.getMemberById(author).getProperty('email')
send_from_address = sender.getProperty('email')

sender_id = "%s (%s), %s" % (sender.getProperty('fullname'), sender.getId(), send_from_address)

host = context.MailHost # plone_utils.getMailHost() (is private)
encoding = plone_utils.getSiteEncoding()

## TODO:
##
## Add fullname, memberid to sender 
variables = {'send_from_address' : send_from_address,
             'sender_id'         : sender_id,
             'url'               : referer,
             'subject'           : subject,
             'message'           : message
             }

try:
    message = context.author_feedback_template(context, **variables)
    result = host.secureSend(message, send_to_address, send_from_address, subject=subject, subtype='plain', charset=encoding, debug=False)
except ConflictError:
    raise
except: #XXX Too many things could possibly go wrong. So we catch all.
    exception = context.plone_utils.exceptionString()
    return state.set(status='failure', portal_status_message='Unable to send mail: ' + exception)

tmsg='Sent feedback from %s to %s' % ('x', 'y')
transaction_note(tmsg)

## clear request variables so form is cleared as well
REQUEST.set('message', None)
REQUEST.set('subject', None)

state.set(portal_status_message='Mail sent.')
return state
