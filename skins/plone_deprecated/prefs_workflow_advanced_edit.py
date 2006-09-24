## Script (Python) "prefs_workflow_advanced_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=wf
##title=
##

context.plone_log("The prefs_workflow_advanced_edit script is deprecated and "
                  "will be removed in Plone 3.5.")

# Import a standard function, and get the HTML request and response objects.
from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

for w in wf.keys():
    context.portal_workflow.setChainForPortalTypes((w,), wf[w])
return context.prefs_workflow_advanced()
