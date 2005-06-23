## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Personalization Handler.

from Products.CMFPlone import transaction_note

member=context.portal_membership.getAuthenticatedMember()

context.portal_membership.deletePersonalPortrait(member.getId())


tmsg='Deleted portrait for %s' % (member.getUserName())
transaction_note(tmsg)

context.plone_utils.addPortalMessage('Your portrait has been deleted.')
return state
