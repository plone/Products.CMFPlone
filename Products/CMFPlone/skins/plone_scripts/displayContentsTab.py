## Script (Python) "displayContentsTab"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

# We won't deprecate this just yet, because people expect it to be acquired
# from context and frequently override it on their content classes.
return context.restrictedTraverse('@@plone').displayContentsTab()
