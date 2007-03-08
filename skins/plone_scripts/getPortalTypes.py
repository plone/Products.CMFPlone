## Script (Python) "getPortalTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return a list of the content types installed in the portal

from Products.CMFCore.utils import getToolByInterfaceName

portal_types_tool=getToolByInterfaceName('Products.CMFCore.interfaces.ITypesTool')
installed_types=portal_types_tool.listContentTypes()

return installed_types

