## Script (Python) "prefs_user_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, portrait='',delete_portrait=''
##title=Edit user
##

from Products.CMFPlone import PloneMessageFactory as _

#update portrait
REQUEST=context.REQUEST
portal_membership = context.portal_membership
member=portal_membership.getMemberById(userid)
if portrait:
    portrait.seek(0)
    portal_membership.changeMemberPortrait(portrait, userid)

if delete_portrait:
    context.portal_membership.deletePersonalPortrait(member.getId())

processed={}
for id, property in context.portal_memberdata.propertyItems():
    if id == 'last_login_time':
        continue
    if id in REQUEST:
        processed[id] = REQUEST.get(id)

if not processed.get('visible_ids'):
    processed['visible_ids'] = 0

context.plone_utils.setMemberProperties(member, REQUEST=REQUEST, **processed)

context.plone_utils.addPortalMessage(_(u'Changes made.'))
return state
