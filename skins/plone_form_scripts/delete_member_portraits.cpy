## Controller Python Script "delete_member_portraits"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=ids=[]
##title=Delete member portraits

from Products.CMFPlone import transaction_note
from Products.CMFCore.utils import getToolByName

membership = getToolByName(context, 'portal_membership')

for member in ids:
    membership.deletePersonalPortrait(member)


tmsg='Deleted portrait(s) of %s.' % ' '.join(ids)
transaction_note(tmsg)

return state.set(portal_status_message=tmsg)
