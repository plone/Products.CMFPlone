## Script (Python) "batchedFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,suppressHiddenFiles=1
##title=wrapper method around listFolderContents (batched)
##

# Since we are startng to call listFolderContents on
# Folderish objects so that we can suppress content whose
# id starts with a . - we need a method to do this.
# Mainly because Portal.py inherients from PortalFolder
# and not PloneFolder.  But there could many other
# instances of 3rd party products that do the same thing.
# so here is the method.

contents = None
try:
    contents = context.aq_explicit.listFolderContents(contentFilter=contentFilter, suppressHiddenFiles=suppressHiddenFiles)
except TypeError:
    #XXX Manually do suppression
    context.plone_log('Manual fall back in getFolderContents - your Folder.listFolderContents method does not ' \
                      'support suppressHiddenFiles')
    contents = [obj for obj in context.aq_explicit.listFolderContents(contentFilter=contentFilter) if obj.getId()[:1]!='.']

from Products.CMFPlone import Batch
b_start = context.REQUEST.get('b_start', 0)
batch = Batch(contents, 100, int(b_start), orphan=0)
return batch
