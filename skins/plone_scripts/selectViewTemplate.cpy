## Script (Python) "selectViewTemplate"
##title=Helper method to select a view template
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=templateId

from Products.CMFCore.utils import getToolByName

IBROWSERDEFAULT = 'Products.CMFPlone.interfaces.BrowserDefault.IBrowserDefault'

itool = getToolByName(context, 'portal_interface')

# This should never happen, but let's be informative if it does
if not itool.objectImplements(context, IBROWSERDEFAULT):
    raise NotImplementedError, "Object does not support IBrowserDefault"

context.setLayout(templateId)

return state.set(portal_status_message = 'View changed')