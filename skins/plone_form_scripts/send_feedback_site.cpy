## Controller Python Script "send_feedback_site"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Send feedback to portal administrator
##
REQUEST=context.REQUEST

from Products.CMFPlone import transaction_note
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
subject = REQUEST.get('subject', '')
message = REQUEST.get('message', '')
referer = REQUEST.get('referer', '')

sender = mtool.getAuthenticatedMember()

site_properties = getToolByName(context, 'portal_properties').site_properties
send_to_address = site_properties.email_from_address

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
	     'referer'           : referer,
             'subject'           : subject,
             'message'           : message
             }

try:
    message = context.site_feedback_template(context, **variables)
    result = host.secureSend(message, send_to_address, send_from_address, subject=subject, subtype='plain', charset=encoding, debug=False)
except ConflictError:
    raise
except: #XXX Too many things could possibly go wrong. So we catch all.
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
