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

parent = context.aq_parent
show = 1
#We only want to show the 'contents' tab under the following conditions:
# - If you can DO SOMETHING in a folder_contents view. i.e.
#   Copy or Move, or Modify portal content, or Add portal content.
# - If you can not do that in the current context, check the container
#   to see if you can do SOMETHING
for permission in ('Copy or Move',
                   'List folder contents',
                   'Modify portal content'):
    if not checkPermission(permission, context):
        show = 0
        break

if not show and (not checkPermission('Modify portal content', parent) or \
                 not checkPermission('Copy or Move', parent)):
    return 0

return 1
