## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=portrait=None
##title=Personalization Handler.

from Products.CMFPlone import transaction_note
#portrait_id='MyPortrait'
state = context.portal_form_controller.getState(script, is_validator=0)

member=context.portal_membership.getAuthenticatedMember()
member.setProperties(context.REQUEST)
member_context=context.portal_membership.getHomeFolder(member.getId())
context.portal_skins.updateSkinCookie()

if member_context is None:
    member_context=context.portal_url.getPortalObject()

if (portrait and portrait.filename):
    context.portal_membership.changeMemberPortrait(portrait)

tmsg=member.getUserName()+' personalized their settings.'
transaction_note(tmsg)

return state.set(portal_status_message='Your personal settings have been saved.')
