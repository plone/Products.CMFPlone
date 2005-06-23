## Script (Python) "prefs_user_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=userid, portrait='',delete_portrait=''
##title=Edit user
##
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
    if REQUEST.has_key(id):
        processed[id] = REQUEST.get(id)

if not processed.get('ext_editor'):
    processed['ext_editor'] = ''

if not processed.get('listed'):
    processed['listed'] = ''
context.plone_utils.setMemberProperties(member, **processed)

context.plone_utils.addPortalMessage('Changes made.')
return state
