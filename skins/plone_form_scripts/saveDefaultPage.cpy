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
from Products.CMFPlone import PloneMessageFactory as _

if not objectId:
    context.plone_utils.addPortalMessage(_(u'Please select an item to use'))
    return state.set(status = 'missing')

from Products.CMFCore.utils import getToolByName
itool = getToolByName(context, 'portal_interface')

# Should never happen, but let's be sure
if not itool.objectImplements(context, INTERFACE):
    raise NotImplementedError, "Object does not support setting default page"

# Also should never happen
if not objectId in context.objectIds():
    message = _(u'There is no object with short name ${name} in this folder.',
                mapping={u'name' : objectId})
    
    context.plone_utils.addPortalMessage(message)
    return state.set(status = 'failure')

context.setDefaultPage(objectId)

context.plone_utils.addPortalMessage(_(u'View changed.'))
return state
