## Script (Python) "getFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,suppressHiddenFiles=1
##title=wrapper method around listFolderContents
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
    contents = context.listFolderContents(contentFilter=contentFilter, suppressHiddenFiles=suppressHiddenFiles)
except TypeError:
    #XXX Manually do suppression
    contents = [obj for obj in context.listFolderContents(contentFilter=contentFilter) if obj.getId()[:1]!='.']
return contents

