## Script (Python) "selectDefaultPage"
##title=Helper method to select a default page for a folder view
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=objectId=None

INTERFACE = 'Products.CMFPlone.interfaces.BrowserDefault.ISelectableBrowserDefault'

if not objectId:
    return state.set(status = 'missing',
                     portal_status_message = 'Please select an item to use')    

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')

# Should never happen, but let's be sure
if not itool.objectImplements(context, INTERFACE):
    raise NotImplementedError, "Object does not support setting default page"

# Also should never happen
if not objectId in context.objectIds():
    return state.set(status = 'failure',
                     portal_status_message = \
                        'There is no object with short name %s in this folder' \
                            % objectId)

context.setDefaultPage(objectId)

return state.set(portal_status_message = 'View changed')