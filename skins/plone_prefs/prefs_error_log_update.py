## Script (Python) "prefs_error_log_update"
## Giorgio, Lorty - Plone Castle Sprint

from Products.CMFPlone import PloneMessageFactory as _

request=context.REQUEST
membership_tool=context.portal_membership
member=membership_tool.getAuthenticatedMember()

if (request['submit']=="Show all entries"):
    member.setProperties(error_log_update=0.0)
    context.plone_utils.addPortalMessage(_(u'Showing all entries'))
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
elif (request['submit']=="Clear Displayed Entries"):
    member.setProperties(error_log_update=DateTime().timeTime())
    context.plone_utils.addPortalMessage(_(u'Entries cleared'))
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
else:
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
