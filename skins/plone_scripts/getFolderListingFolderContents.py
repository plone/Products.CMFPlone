## Script (Python) "getFolderListingFolderContents"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=contentFilter=None,suppressHiddenFiles=1
##title=wrapper method around listFolderContents
##

# The difference between this script and getFolderContents.py
# is that it calls folderlistingFolderContents instead of
# listFolderContents.  This way folder_listing can be seen
# by those without 'List folder contents' permission since that
# is only meant to protect the folder_contents page.

# Since we are startng to call listFolderContents on
# Folderish objects so that we can suppress content whose
# id starts with a . - we need a method to do this.
# Mainly because Portal.py inherients from PortalFolder
# and not PloneFolder.  But there could many other
# instances of 3rd party products that do the same thing.
# so here is the method.

contents = None
try:
    contents = context.folderlistingFolderContents(contentFilter=contentFilter, suppressHiddenFiles=suppressHiddenFiles)
except AttributeError:
    try:
        contents = context.listFolderContents(contentFilter=contentFilter, suppressHiddenFiles=suppressHiddenFiles)
    except TypeError:
        #XXX Manually do suppression
        context.plone_log('Manual fall back in getFolderContents - your Folder.listFolderContents method does not ' \
                          'support suppressHiddenFiles')
        contents = [obj
                    for obj in context.listFolderContents(contentFilter=contentFilter)
                    if not obj.getId().startswith('.')
                   ]
except TypeError:
    #XXX Manually do suppression
    context.plone_log('Manual fall back in getFolderContents - your Folder.listFolderContents method does not ' \
                      'support suppressHiddenFiles')
    contents = [obj
                for obj in context.listFolderContents(contentFilter=contentFilter)
                if not obj.getId().startswith('.')
               ]
return contents
