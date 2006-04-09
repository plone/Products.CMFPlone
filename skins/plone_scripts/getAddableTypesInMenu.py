## Script (Python) "getAddableTypesInMenu"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=allowedTypes
##title=Return a list of the content type ftis filtered by getImmediatelyAddableTypes(), if available.

INTERFACE = "Products.CMFPlone.interfaces.ConstrainTypes.IConstrainTypes"

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')
mtool = getToolByName(context, 'portal_membership')

plone_view = context.restrictedTraverse('@@plone')
folder = plone_view.getCurrentFolder()

if not itool.objectImplements(folder, INTERFACE):
    return allowedTypes

if mtool.checkPermission('View', folder):
    immediateIds = folder.getImmediatelyAddableTypes()
    return [ctype for ctype in allowedTypes if ctype.getId() in immediateIds]
else:
    return []

