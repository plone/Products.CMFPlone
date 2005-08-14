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
list_permission = 'List folder contents'
modification_permissions = ('Modify portal content',
                            'Add portal content',
                            'Copy or Move',
                            'Delete objects',
                            'Review portal content')

contents_object = context
# If this object is not folderish or is the parent folder's default page,
# then the folder_contents action is for the parent, check permissions there.
if contents_object.isDefaultPageInFolder():
    try:
        contents_object = contents_object.getParentNode()
    except Unauthorized:
        return 0

# If this is not a structural folder, that is a folderish item which should be
# treated as such for navigation purposes (not just as an implementation detail)
# stop.
if not contents_object.is_folderish():
    return 0

show = 0
#We only want to show the 'batch' action under the following conditions:
# - If you have permission to list the contents of the relavant object, and
#   you can DO SOMETHING in a folder_contents view. i.e.
#   Copy or Move, or Modify portal content, Add portal content,
#   or Delete objects.

# Require 'List folder contents' on the current object
if checkPermission(list_permission, contents_object):
    # If any modifications are allowed on object show the tab.
    for permission in modification_permissions:
        if checkPermission(permission, contents_object):
            show = 1
            break

return show