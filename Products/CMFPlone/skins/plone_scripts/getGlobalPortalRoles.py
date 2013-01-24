## Script (Python) "getGlobalPortalRoles"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

return [r for r in context.portal_membership.getPortalRoles() if r != 'Owner']
