## Script (Python) "keyFilteredActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=actions=None
##title=
##

#If action does not have an ID it will not
#show up in the keyedActions.

context.plone_log("The keyFilteredActions script is deprecated and will be "
                  "removed in Plone 4.0.  Use the keyFilteredActions method "
                  "of the @@plone view instead.")

return context.restrictedTraverse('@@plone').keyFilteredActions(actions)
