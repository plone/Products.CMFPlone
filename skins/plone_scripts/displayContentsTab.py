## Script (Python) "displayContentsTab"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from AccessControl import Unauthorized

pm=context.portal_membership
checkPermission=pm.checkPermission

try:
    parent = context.aq_parent
except Unauthorized:
    parent = None

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

if not show and parent is not None:
    for permission in ('Copy or Move',
                       #'List folder contents',
                       'Modify portal content'):
        if not checkPermission(permission, parent):
            return 0

return 1
