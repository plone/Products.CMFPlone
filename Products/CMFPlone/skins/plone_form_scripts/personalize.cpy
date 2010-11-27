## Controller Python Script "personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=visible_ids=None, portrait=None, REQUEST=None, ext_editor=None, listed=None
##title=Personalization Handler.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import transaction_note, set_own_login_name
from Products.CMFPlone import PloneMessageFactory as _

member=context.portal_membership.getAuthenticatedMember()
member.setProperties(properties=context.REQUEST, REQUEST=REQUEST)
member_context=context.portal_membership.getHomeFolder(member.getId())
context.portal_skins.updateSkinCookie()

if member_context is None:
    member_context=context.portal_url.getPortalObject()

if visible_ids is None and REQUEST is not None:
    visible_ids=0
else:
    visible_ids=1
REQUEST.set('visible_ids', visible_ids)

if ext_editor is None and REQUEST is not None:
    ext_editor=0
else:
    ext_editor=1
REQUEST.set('ext_editor', ext_editor)

if listed is None and REQUEST is not None:
    listed=0
else:
    listed=1
REQUEST.set('listed', listed)

if (portrait and portrait.filename):
    context.portal_membership.changeMemberPortrait(portrait)

delete_portrait = context.REQUEST.get('delete_portrait', None)
if delete_portrait:
    context.portal_membership.deletePersonalPortrait(member.getId())

email = context.REQUEST.get('email')
if email:
    props = getToolByName(context, 'portal_properties').site_properties
    if props.getProperty('use_email_as_login'):
        try:
            set_own_login_name(member, email)
        except KeyError:
            # Probably user in zope root
            pass

member.setProperties(ext_editor=ext_editor, listed=listed, visible_ids=visible_ids)

tmsg='Edited personal settings for %s' % member.getId()
transaction_note(tmsg)

context.plone_utils.addPortalMessage(_(u'Your personal settings have been saved.'))
return state
