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

INTERFACE = 'Products.CMFPlone.interfaces.BrowserDefault.ISelectableBrowserDefault'

itool = getToolByName(context, 'portal_interface')

# This should never happen, but let's be informative if it does
if not itool.objectImplements(context, INTERFACE):
    raise NotImplementedError, "Object does not support selecting layout templates"

context.setLayout(templateId)

message = context.translate(msgid="message_view_changed",
                            default="View changed.")
return state.set(portal_status_message=message)
