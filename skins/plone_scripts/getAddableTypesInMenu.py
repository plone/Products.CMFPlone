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

folder = context
if not folder.isPrincipiaFolderish:
    folder = context.aq_inner.aq_parent

if not itool.objectImplements(folder, INTERFACE):
    return allowedTypes

immediateIds = folder.getImmediatelyAddableTypes()
return [ctype for ctype in allowedTypes if ctype.getId() in immediateIds]

