## Script (Python) ""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=users=[], resetpassword=[], delete=[]
##title=Edit users
##

acl_users = context.acl_users
getMemberById = context.portal_membership.getMemberById
mailPassword = context.portal_registration.mailPassword
setMemberProperties = context.plone_utils.setMemberProperties
generatePassword = context.portal_registration.generatePassword

for user in users:
    # Don't bother if the user will be deleted anyway
    if user.id in delete:
        continue

    member = getMemberById(user.id)
    # If email address was changed, set the new one
    if user.email != member.getProperty('email'):
        setMemberProperties(member, email=user.email)

    # If reset password has been checked email user a new password
    if hasattr(user, 'resetpassword'):
        pw = generatePassword()
    else:
        pw = None
        
    acl_users.userFolderEditUser(user.id, pw, user.get('roles',[]), member.getDomains())
    if pw:
        mailPassword(user.id, context.REQUEST)

if delete:
    acl_users.userFolderDelUsers(delete)

context.plone_utils.addPortalMessage(context.translate('Changes applied.'))
context.REQUEST.stripFormData() # fix issue 3835
return state
