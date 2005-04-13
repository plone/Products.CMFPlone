## Script (Python) "getFolderListingFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,suppressHiddenFiles=1
##title=wrapper method around listFolderContents
##
from zLOG import LOG, WARNING
# XXX DEPRECATION ahead!
LOG('Plone Debug', WARNING, 'The batchedFolderContents script is DEPRECATED, '
                            'and will be removed in plone 2.3. Please use '
                            'getFolderContents with the parameter batch=True')

batch = context.getFolderContents(contentFilter, batch=True)
return batch