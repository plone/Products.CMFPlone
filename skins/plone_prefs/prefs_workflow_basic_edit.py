## Script (Python) "prefs_workflow_basic_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default_workflow=None
##title=
##
# Example code:

# Import a standard function, and get the HTML request and response objects.
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

if default_workflow:
    context.portal_workflow.setChainForPortalTypes(
        context.portal_types.listContentTypes(),
        default_workflow,
	REQUEST = context.REQUEST)

return context.prefs_workflow_basic()
