## Script (Python) "isDefaultPageInFolder"
##title=Find out if the current context is the default page in its parent
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
context.plone_log("The isDefaultPageInFolder script is deprecated and will be"
                  " removed in Plone 4.0.  Use the isDefaultPageInFolder "
                  "method of the @@plone view instead.")

return context.restrictedTraverse('@@plone').isDefaultPageInFolder()
