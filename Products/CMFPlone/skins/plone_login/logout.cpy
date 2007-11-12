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

REQUEST = context.REQUEST

mt = getToolByName(context, 'portal_membership')
mt.logoutUser(REQUEST=REQUEST)

from Products.CMFPlone.utils import transaction_note
transaction_note('Logged out')

target_url = REQUEST.URL1
# Double '$' to avoid injection into TALES
target_url = target_url.replace('$','$$')
target_url += '/logged_out'
return state.set(next_action='redirect_to:string:' + target_url )
