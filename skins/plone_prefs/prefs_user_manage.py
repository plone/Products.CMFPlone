## Script (Python) ""
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Edit users
##
REQUEST=context.REQUEST
acl_users=context.acl_users
getMemberById=context.portal_membership.getMemberById
mailPassword=context.portal_registration.mailPassword
setMemberProperties=context.plone_utils.setMemberProperties
generatepassword=context.portal_registration.generatePassword
removed=REQUEST.get('delete', [])
resetpw=REQUEST.get('resetpassword', [])

#parse REQUEST - yuk!
originals={}
entered={}
for key in REQUEST.keys():
    if key.startswith('email_'):        
        email=REQUEST[key]
        if key.startswith('email_original_'):
            username=key[len('email_original_'):]
            originals[username]=email
        if key.startswith('email_entered_'):
            username=key[len('email_entered_'):]
            entered[username]=email

#booleans act differently; they do not show up in the REQUEST
#if they are unchecked.  So we need to iterate over the properties
#and if they are boolean and not found in REQUEST then we give them 0 value

#if a email address was changed setProperty
for userid,email in originals.items():
    if email!=entered[userid]:
        setMemberProperties(userid, email=entered[userid])


#raise(context.REQUEST)

for key in REQUEST.keys():
    if key.startswith('roles-'):
        userid=key[len('roles-'):]
        member=getMemberById(userid)
        roles=[role for role in REQUEST[key] if role]
        domains=''
        if hasattr(member, 'getDomains'):
            domains=member.getDomains()
        acl_users.userFolderEditUser(userid, None, roles, domains)

#reset password has been checked; email password
for userid in resetpw:
    if userid in removed:
        continue
    pw = generatepassword()
    member = acl_users.getUserById(userid)
    acl_users.userFolderEditUser(userid, pw, member.getRoles(), member.getDomains())
    mailPassword(userid, context.REQUEST)

#if remove user was checked
if removed:
    acl_users.userFolderDelUsers(removed)
        
url='%s?%s' % (REQUEST.HTTP_REFERER,
               'portal_status_message=Changes+made.')
return REQUEST.RESPONSE.redirect(url)
