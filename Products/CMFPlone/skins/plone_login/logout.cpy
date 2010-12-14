## Controller Python Script "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Logout handler
##parameters=

from Products.CMFCore.utils import getToolByName

request = context.REQUEST

mt = getToolByName(context, 'portal_membership')
mt.logoutUser(request)

from Products.CMFPlone.utils import transaction_note
transaction_note('Logged out')

# Handle external logout requests from other portals
next = request.get('next', None)
if (next is not None and context.portal_url.isURLInPortal(next)):
    target_url = next
else:
    target_url = request.URL1 + '/logged_out'
    site_properties = context.portal_properties.site_properties
    external_logout_url = site_properties.getProperty('external_logout_url')
    if external_logout_url:
        target_url = "%s?next=%s" % (external_logout_url, target_url)

# Double '$' to avoid injection into TALES
target_url = target_url.replace('$','$$')
return state.set(next_action='redirect_to:string:' + target_url )
