## Script (Python) "getSelectableViews"
##title=Get the view templates available from TemplateMixin on the context, if there is more than one
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

ITEMPLATEMIXIN = 'Products.Archetypes.interfaces.ITemplateMixin.ITemplateMixin'
MODIFY_VIEW_TEMPLATE = "ATContentTypes: Modify view template"

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')
mtool = getToolByName(context, 'portal_membership')

if not itool.objectImplements(context, ITEMPLATEMIXIN):
    return None

user = mtool.getAuthenticatedMember()
if not user.has_permission(MODIFY_VIEW_TEMPLATE, context):
    return None
    
availableTemplates = context.getField('layout').Vocabulary(context)
if len(availableTemplates) <= 1:
    return None

return availableTemplates