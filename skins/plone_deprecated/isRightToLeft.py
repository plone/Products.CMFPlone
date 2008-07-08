## Script (Python) "isRightToLeft"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=domain
##title=
##
context.plone_log("The isRightToLeft script is deprecated and will be "
                  "removed in Plone 4.0.  Use the isRightToLeft method "
                  "of the @@plone view instead.")

return context.restrictedTraverse('@@plone').isRightToLeft(domain)
