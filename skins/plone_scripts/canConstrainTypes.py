## Script (Python) "canConstrainTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Find out if the context supports per-instance addable type restriction 

INTERFACE = 'Products.CMFPlone.interfaces.ConstrainTypes.ISelectableConstrainTypes'
from Products.CMFCore.utils import getToolByName

itool = getToolByName(context, 'portal_interface')
if not itool.objectImplements(context, INTERFACE):
    return False

return context.canSetConstrainTypes()
