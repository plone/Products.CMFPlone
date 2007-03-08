## Script (Python) "canSelectDefaultPage"
##title=Find out if a default page can be selected on this folderish item
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
from AccessControl import Unauthorized

INTERFACE = 'Products.CMFPlone.interfaces.BrowserDefault.ISelectableBrowserDefault'

# It's silly but because this is often called on the parent folder, we must
# ensure we have permission.
try:
    if not context.isPrincipiaFolderish:
        return False
except Unauthorized:
        return False

from Products.CMFCore.utils import getToolByInterfaceName
itool = getToolByInterfaceName('Products.CMFPlone.interfaces.IInterfaceTool')

if not itool.objectImplements(context, INTERFACE):
    return False
    
return context.canSetDefaultPage()
