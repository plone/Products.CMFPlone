## Script (Python) "prefs_group_manage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Manage groups
##
REQUEST=context.REQUEST
acl_users=context.acl_users

groups=[group[len('group_'):] 
        for group in REQUEST.keys() 
        if group.startswith('group_')]

for group in groups:
    roles=REQUEST['group_'+group]
    acl_users.Groups.acl_users.userFolderEditUser(group, None, roles, ())

delete=[group[len('group_'):]
        for group in REQUEST.get('delete',[])
        if group and group.startswith('group')]

acl_users.Groups.acl_users.userFolderDelUsers(delete)
    
url='%s?%s' % (REQUEST.HTTP_REFERER,
               'portal_status_message=Changes+made.')
return REQUEST.RESPONSE.redirect(url)
