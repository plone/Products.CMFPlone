## Script (Python) "selectDefaultPage"
##title=Helper method to select a default page for a folder view
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=objectId=None

ISELECTABLEDEFAULTPAGE = 'Products.ATContentTypes.interfaces.ISelectableDefaultPage'
DEFAULT_PAGE = 'default_page'

if not objectId:
    return state.set(status = 'missing',
                     portal_status_message = 'Please select an item to use')    

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')
mtool = getToolByName(context, 'portal_membership')

if not itool.objectImplements(context, ISELECTABLEDEFAULTPAGE):
    raise NotImplementedError, "Object does not support setting default page"

if not objectId in context.objectIds():
    return state.set(status = 'failure',
                     portal_status_message = \
                        'There is no object with short name %s in this folder' % objectId)

if context.hasProperty(DEFAULT_PAGE):
    context.manage_changeProperties(default_page = objectId)
else:
    context.manage_addProperty(DEFAULT_PAGE, objectId, 'string')

return state.set(portal_status_message = 'View changed')