## Script (Python) "canSelectDefaultPage"
##title=Find out if a default page can be selected on this folderish item
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

ISELECTABLEDEFAULTPAGE = 'Products.ATContentTypes.interfaces.ISelectableDefaultPage'
MODIFY = "Modify portal content"

if not context.isPrincipiaFolderish:
    return False

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')
mtool = getToolByName(context, 'portal_membership')

if not itool.objectImplements(context, ISELECTABLEDEFAULTPAGE):
    return False

user = mtool.getAuthenticatedMember()
if not user.has_permission(MODIFY, context):
    return False
    
return True