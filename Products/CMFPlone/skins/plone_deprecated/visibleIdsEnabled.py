## Script (Python) "visibleIdsEnabled"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.plone_log("The visibleIdsEnabled script is deprecated and will be "
                  "removed in Plone 4.0.  Use the visibleIdsEnabled method "
                  "of the @@plone view instead.")

return context.restrictedTraverse('@@plone').visibleIdsEnabled()
