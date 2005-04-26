## Script (Python) "canSelectDefaultPage"
##title=Find out if a default page can be selected on this folderish item
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

INTERFACE = 'Products.CMFPlone.interfaces.BrowserDefault.ISelectableBrowserDefault'

if not context.isPrincipiaFolderish:
    return False

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')

if not itool.objectImplements(context, INTERFACE):
    return False
    
return context.canSetDefaultPage()