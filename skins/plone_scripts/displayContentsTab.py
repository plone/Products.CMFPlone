## Script (Python) "displayContentsTab"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

pm=context.portal_membership
checkPermission=pm.checkPermission
for permission in ('List folder contents',
                   'Modify portal content',
                   'Copy or Move'):
    if not checkPermission(permission, context):
        return 0
return 1
