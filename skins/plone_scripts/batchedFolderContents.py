## Script (Python) "batchedFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,suppressHiddenFiles=1
##title=wrapper method around listFolderContents
##
from Products.CMFPlone.utils import log_deprecated
# XXX DEPRECATION ahead!
log_deprecated('The batchedFolderContents script is deprecated '
               'and will be removed in Plone 2.2. Please use '
               'getFolderContents with the parameter batch=True.')
return context.getFolderContents(contentFilter, batch=True, full_objects=True)
