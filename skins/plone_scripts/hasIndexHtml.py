## Script (Python) "hasIndexHtml"
##title=Find out if this folder has an index_html page
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
from AccessControl import Unauthorized
# It's silly but because this is often called on the parent folder, we must
# ensure we have permission.
try:
    if not context.isPrincipiaFolderish:
        return False
except Unauthorized:
        return False

if 'index_html' in context.objectIds():
    return True
else:
    return False
    
    
