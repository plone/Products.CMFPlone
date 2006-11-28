## Script (Python) "hasIndexHtml"
##title=Find out if this folder has an index_html page
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
from AccessControl import Unauthorized
from Products.CMFPlone.utils import base_hasattr
# It's silly but because this is often called on the parent folder, we must
# ensure we have permission.
try:
    if not context.isPrincipiaFolderish:
        return False
except Unauthorized:
    return False

# Use the BTreeFolder API if possible
if base_hasattr(context, 'has_key'):
    # BTreeFolder's has_key returns numeric values
    return context.has_key('index_html') and True or False
elif 'index_html' in context.objectIds():
    return True
else:
    return False
