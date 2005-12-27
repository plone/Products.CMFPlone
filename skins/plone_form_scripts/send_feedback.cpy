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

from Products.CMFPlone.utils import transaction_note
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

##
## This may change depending on the called (portal_feedback or author)
state_success = "success"
state_failure = "failure"


plone_utils = getToolByName(context, 'plone_utils')
mtool = getToolByName(context, 'portal_membership')

site_properties = getToolByName(context, 'portal_properties').site_properties

## make these arguments?
referer = REQUEST.get('referer', 'unknown referer')
subject = REQUEST.get('subject', '')
message = REQUEST.get('message', '')
author = REQUEST.get('author', None) # None means portal administrator

sender = mtool.getAuthenticatedMember()

site_properties = getToolByName(context, 'portal_properties').site_properties
envelope_from = site_properties.email_from_address

if author is None:
    send_to_address = site_properties.email_from_address
else:
    send_to_address = mtool.getMemberById(author).getProperty('email')
    state_success = "success_author"
    state_failure = "failure_author"

state.set(status=state_success) ## until proven otherwise

send_from_address = sender.getProperty('email')

if send_from_address == '':
    # happens if you don't exist as user in the portal (but at a higher level)
    # or if your memberdata is incomplete.
    # Would be nicer to check in the feedback form, but that's hard to do securely
    return state.set(status=state_failure, portal_status_message="Could not find a valid email address")
    
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
             'message'           : message,
	     'encoding'          : encoding,
             }

try:
    message = context.author_feedback_template(context, **variables)
    result = host.secureSend(message, send_to_address, envelope_from, subject=subject, subtype='plain', charset=encoding, debug=False, From=send_from_address)
except ConflictError:
    raise
except: # TODO Too many things could possibly go wrong. So we catch all.
    exception = context.plone_utils.exceptionString()
    message = context.translate("Unable to send mail: ${exception}",
                                {'exception': exception})
    return state.set(status=state_failure, portal_status_message=message)

tmsg='Sent feedback from %s to %s' % ('x', 'y')
transaction_note(tmsg)

## clear request variables so form is cleared as well
REQUEST.set('message', None)
REQUEST.set('subject', None)

state.set(portal_status_message='Mail sent.')
return state
