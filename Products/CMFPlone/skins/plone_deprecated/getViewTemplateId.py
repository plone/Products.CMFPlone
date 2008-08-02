## Script (Python) "getViewTemplateId"
##title=Get the id of the current view template of the context
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
context.plone_log("The getViewTemplateId script is deprecated and will be "
                  "removed in Plone 4.0. Use the getViewTemplateId method "
                  "of the @@plone view instead.")

return context.restrictedTraverse('@@plone').getViewTemplateId()