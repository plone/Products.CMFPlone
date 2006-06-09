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

try:
    context.acl_users.logout(context.REQUEST)
except:
    pass  # XXX we expect Unauthorized, but why do we do a bare except then?

REQUEST = context.REQUEST


# Invalidate existing sessions, but only if they exist.
sdm = getToolByName(context, 'session_data_manager', None)
if sdm is not None:
    session = sdm.getSessionData(create=0)
    if session is not None:
        session.invalidate()

from Products.CMFPlone.utils import transaction_note
transaction_note('Logged out')

target_url = REQUEST.URL1
# Double '$' to avoid injection into TALES
target_url = target_url.replace('$','$$')
target_url += '/logged_out'
return state.set(next_action='redirect_to:string:' + target_url )
