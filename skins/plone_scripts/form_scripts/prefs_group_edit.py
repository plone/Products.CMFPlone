## Script (Python) "prefs_group_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groupname
##title=Edit user
##
REQUEST=context.REQUEST
acl_users=context.acl_users
prefix=acl_users.getGroupPrefix()
groups=acl_users.getGroups()
users=acl_users.getUsers()

assignedroles=REQUEST.get('roles',[])
assignedusers=REQUEST.get('users',[])
domains=()

if groupname not in groups:
    acl_users.Groups.acl_users.userFolderAddUser(groupname, '', (), domains)

if assignedroles:
    acl_users.Groups.acl_users.userFolderEditUser(groupname,
                                                  None,
                                                  tuple(assignedroles),
                                                  domains)
    
for user in assignedusers:
    userobject=acl_users.getUser(user)
    if groupname not in userobject.getGroups():
        acl_users.Users.acl_users.userFolderEditUser(user, 
                                                     None, 
                                                     userobject.getRoles()+(prefix+groupname,),
                                                     domains)

#no roles were selected, remove them from group
if not assignedroles:
    acl_users.Groups.acl_users.userFolderEditUser(groupname,
                                                  None,
                                                  (),
                                                  domains)

#no users were selected, iterate over users and remove the role if they had it
if not assignedusers:
    for user in acl_users.getUsers():
        usergroups=list( user.getGroups() )
        try:
            usergroups.remove(prefix+groupname)
            acl_users.Users.acl_users.userFolderEditUser(user.getId(),
                                                        None,
                                                        user.getRoles()+tuple(usergroups),
                                                        domains)
        except ValueError:
            #groupname was not found in user's Groups
            pass
            
REFERER=REQUEST.HTTP_REFERER

if REFERER.find('portal_status_message')!=-1:
    REFERER=REFERER[:REFERER.find('portal_status_message')]
    
url='%s&%s' % (REFERER, 'portal_status_message=Changes+made.')
return REQUEST.RESPONSE.redirect(url)
