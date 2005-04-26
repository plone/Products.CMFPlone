## Script (Python) "getSelectableViews"
##title=Get the view templates available from BrowserDefaultMixin on the context, if there is more than one
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

layouts = context.getAvailableLayouts()

if len(layouts) > 1:
    return layouts
else:
    return None