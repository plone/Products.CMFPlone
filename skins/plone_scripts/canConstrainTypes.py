## Script (Python) "canConstrainTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Find out if the context supports per-instance addable type restriction 

# XXX: This may eventually move to Archetypes core
ICONSTRAINTYPESMIXIN = 'Products.ATContentTypes.interfaces.IConstrainTypes'
MODIFY_TYPE_CONSTRAINTS = "ATContentTypes: Modify constrain types"

from Products.CMFCore.utils import getToolByName

itool = getToolByName(context, 'portal_interface')
if not itool.objectImplements(context, ICONSTRAINTYPESMIXIN):
    return False

mtool = getToolByName(context, 'portal_membership')
user = mtool.getAuthenticatedMember()
if not user.has_permission(MODIFY_TYPE_CONSTRAINTS, context):
    return False

return True
