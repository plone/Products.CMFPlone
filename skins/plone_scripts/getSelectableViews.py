## Script (Python) "getSelectableViews"
##title=Get the view templates available from TemplateMixin on the context, if there is more than one
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

IBROWSERDEFAULT = 'Products.CMFPlone.interfaces.BrowserDefault.IBrowserDefault'

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')

if not itool.objectImplements(context, IBROWSERDEFAULT):
    return None

if not context.canSetLayout():
    return None

return context.getAvailableLayouts()