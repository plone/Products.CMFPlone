## Script (Python) "getCurrentUrl"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Return the current full URL including query string
##
context.plone_log("The getCurrentURL script is deprecated and will be "
                  "removed in plone 3.5.  Use the getCurrentURL method "
                  "of the @@plone view instead.")

return context.restrictedTraverse('@@plone').getCurrentUrl()
