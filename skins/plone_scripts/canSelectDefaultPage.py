## Script (Python) "canSelectDefaultPage"
##title=Find out if a default page can be selected on this folderish item
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

IBROWSERDEFAULT = 'Products.CMFPlone.interfaces.BrowserDefault.IBrowserDefault'

if not context.isPrincipiaFolderish:
    return False

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')

if not itool.objectImplements(context, IBROWSERDEFAULT):
    return False
    
return context.canSetDefaultPage()