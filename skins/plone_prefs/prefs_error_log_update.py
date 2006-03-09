## Script (Python) "prefs_error_log_update"
## Giorgio, Lorty - Plone Castle Sprint

request=context.REQUEST
membership_tool=context.portal_membership
member=membership_tool.getAuthenticatedMember()

if hasattr(request, 'form.button.showall'):
    member.setProperties(error_log_update=0.0)
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form?portal_status_message=%s' % ('Showing+all+entries'))
elif hasattr(request, 'form.button.clear'):
    member.setProperties(error_log_update=DateTime().timeTime())
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form?portal_status_message=%s' % ('Entries+cleared'))
else:
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
