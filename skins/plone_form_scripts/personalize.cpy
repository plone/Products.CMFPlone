## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=portrait=None, visible_ids=None, listed=None, REQUEST=None
##title=Personalization Handler.

from Products.CMFPlone import transaction_note
#portrait_id='MyPortrait'

member=context.portal_membership.getAuthenticatedMember()
member.setProperties(context.REQUEST)
member_context=context.portal_membership.getHomeFolder(member.getId())
context.portal_skins.updateSkinCookie()

if member_context is None:
    member_context=context.portal_url.getPortalObject()

if visible_ids is None and REQUEST is not None:    
    REQUEST.set('visible_ids', 0)
    
if listed is None and REQUEST is not None:    
    REQUEST.set('listed', 0)

if (portrait and portrait.filename):
    context.portal_membership.changeMemberPortrait(portrait)

delete_portrait = context.REQUEST.get('delete_portrait', None)
if delete_portrait:
    context.portal_membership.deletePersonalPortrait(member.getId())


tmsg='Edited personal settings for %s' % member.getUserName()
transaction_note(tmsg)

return state.set(portal_status_message='Your personal settings have been saved.')
