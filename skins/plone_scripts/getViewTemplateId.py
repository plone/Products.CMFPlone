## Script (Python) "getViewTemplateId"
##title=Get the id of the current view template of the context
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

INTERFACE = 'Products.CMFPlone.interfaces.BrowserDefault.IBrowserDefault'
from Products.CMFCore.utils import getToolByName

itool = getToolByName(context, 'portal_interface')

# If we have IBrowserDefault, get the selected layout
if itool.objectImplements(context, INTERFACE):
    return context.getLayout()

# Else, if there is a 'folderlisting' action, this will take precedence for
# folders, so try this, else use the 'view' action.

action = context.lookupTypeAction('view')

if not action:
    action = context.lookupTypeAction('folderlisting')

return action