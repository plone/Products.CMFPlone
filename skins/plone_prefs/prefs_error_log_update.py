## Script (Python) "prefs_error_log_update"
## Giorgio, Lorty - Plone Castle Sprint

from Products.CMFPlone import PloneMessageFactory as _
from Products.PythonScripts.standard import url_quote_plus

request=context.REQUEST
membership_tool=context.portal_membership
member=membership_tool.getAuthenticatedMember()

if (request['submit']=="Show all entries"):
    member.setProperties(error_log_update=0.0)
    msg = _(u'Showing all entries')
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form?portal_status_message=%s' % url_quote_plus(msg))
elif (request['submit']=="Clear Displayed Entries"):
    member.setProperties(error_log_update=DateTime().timeTime())
    msg = _(u'Entries cleared')
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form?portal_status_message=%s' % url_quote_plus(msg))
else:
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
