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

DEFAULT_PAGE = 'default_page'
ITEMPLATEVIEWMIXIN = 'Products.Archetypes.interfaces.ITemplateMixin.ITemplateMixin'
ISELECTABLEDEFAULTPAGE = 'Products.ATContentTypes.interfaces.ISelectableDefaultPage'

itool = getToolByName(context, 'portal_interface')

# This should never happen, but let's be informative if it does
if not itool.objectImplements(context, ITEMPLATEVIEWMIXIN):
    raise NotImplementedError, "Object does not support TemplateMixin"

context.setLayout(templateId)

# Remove any default_page property, if set on a folder
if context.isPrincipiaFolderish and context.hasProperty(DEFAULT_PAGE) and \
        itool.objectImplements(context, ISELECTABLEDEFAULTPAGE):
    context.manage_delProperties([DEFAULT_PAGE])

return state.set(portal_status_message = 'View changed')