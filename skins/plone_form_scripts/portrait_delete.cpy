## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Personalization Handler.

from Products.CMFPlone.utils import transaction_note

member=context.portal_membership.getAuthenticatedMember()

context.portal_membership.deletePersonalPortrait(member.getId())


tmsg='Deleted portrait for %s' % (member.getUserName())
transaction_note(tmsg)

return state.set(portal_status_message='Your portrait has been deleted.')
