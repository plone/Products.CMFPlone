## Script (Python) "is_folderish"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Is the context a structural folder
##
context.plone_log("The is_folderish script is deprecated and will be "
                  "removed in plone 3.5.  Use the isStructuralFolder method "
                  "of the @@plone view instead.")

from Products.CMFCore.utils import getToolByName

plone_utils = getToolByName(context, 'plone_utils')
return plone_utils.isStructuralFolder(context)
