## Script (Python) "getGlobalPortalRoles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

local_roles = context.portal_membership.getPortalRoles()

global_roles = []

for local_role in local_roles:
    if local_role != 'Owner':
        global_roles.append(local_role)

return global_roles
