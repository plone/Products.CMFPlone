## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Personalization Handler.

from Products.CMFPlone import transaction_note
state = context.portal_form_controller.getState(script, is_validator=0)

member=context.portal_membership.getAuthenticatedMember()

context.portal_membership.deletePersonalPortrait(member.getId())


tmsg=member.getUserName()+' portrait deleted.'
transaction_note(tmsg)

return state.set(portal_status_message='Your portrait has been deleted.')
