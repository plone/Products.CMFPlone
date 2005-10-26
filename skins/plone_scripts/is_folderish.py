## Script (Python) "is_folderish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Is the context a structural folder
##

from Products.CMFCore.utils import getToolByName

plone_utils = getToolByName(context, 'plone_utils')
return plone_utils.isStructuralFolder(context)
