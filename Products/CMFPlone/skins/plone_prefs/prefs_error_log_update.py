## Script (Python) "prefs_error_log_update"
## Giorgio, Lorty - Plone Castle Sprint

from Products.CMFPlone import PloneMessageFactory as _

request=context.REQUEST
membership_tool=context.portal_membership
member=membership_tool.getAuthenticatedMember()

if getattr(request, 'form.button.search', None) is not None:
    search = request.form.get('search_entry')
    if search == '':
        member.setProperties(error_log_update=0.0)
        context.plone_utils.addPortalMessage(_(u'Showing all entries'))
        return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_showEntry?id=%s' % search)
elif getattr(request, 'form.button.showall', None) is not None:
    member.setProperties(error_log_update=0.0)
    context.plone_utils.addPortalMessage(_(u'Showing all entries'))
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
elif getattr(request, 'form.button.clear', None) is not None:
    member.setProperties(error_log_update=DateTime().timeTime())
    context.plone_utils.addPortalMessage(_(u'Entries cleared'))
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
else:
    return request.RESPONSE.redirect(context.absolute_url() +'/prefs_error_log_form')
