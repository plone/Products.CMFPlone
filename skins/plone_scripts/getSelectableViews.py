## Script (Python) "getSelectableViews"
##title=Get the view templates available from TemplateMixin on the context, if there is more than one
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

INTERFACE = 'Products.CMFPlone.interfaces.BrowserDefault.ISelectableBrowserDefault'

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')

if not itool.objectImplements(context, INTERFACE):
    return None

if not context.canSetLayout():
    return None

return context.getAvailableLayouts()