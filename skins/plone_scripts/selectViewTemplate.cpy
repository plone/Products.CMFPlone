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
from Products.CMFPlone import PloneMessageFactory as _

INTERFACE = 'Products.CMFPlone.interfaces.BrowserDefault.ISelectableBrowserDefault'

itool = getToolByName(context, 'portal_interface')

# This should never happen, but let's be informative if it does
if not itool.objectImplements(context, INTERFACE):
    raise NotImplementedError, "Object does not support selecting layout templates"

context.setLayout(templateId)

context.plone_utils.addPortalMessage(_(u'View changed'))
return state
