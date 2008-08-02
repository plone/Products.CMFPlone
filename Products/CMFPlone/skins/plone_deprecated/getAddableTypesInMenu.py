## Script (Python) "getAddableTypesInMenu"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=allowedTypes
##title=Return a list of the content type ftis filtered by getImmediatelyAddableTypes(), if available.

context.plone_log("The getAddableTypesInMenu script is deprecated and will be "
                  "removed in Plone 4.0.")

INTERFACE = "Products.CMFPlone.interfaces.ConstrainTypes.IConstrainTypes"

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')
mtool = getToolByName(context, 'portal_membership')
translate = context.translate

plone_view = context.restrictedTraverse('@@plone')
folder = plone_view.getCurrentFolder()

if not itool.objectImplements(folder, INTERFACE):
    result = [(translate(ctype.Title()), ctype) for ctype in allowedTypes]
    result.sort()
    result = [ctype[-1] for ctype in result]
    return result

if mtool.checkPermission('View', folder):
    immediateIds = folder.getImmediatelyAddableTypes()
    result = [(translate(ctype.Title()), ctype) for ctype in allowedTypes if ctype.getId() in immediateIds]
    result.sort()
    result = [ctype[-1] for ctype in result]
    return result
else:
    return []
