## Script (Python) "isDefaultPage"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
try:
    return context.plone_utils.browserDefault(context.aq_parent)[1][0] == context.getId()
except (AttributeError,KeyError,IndexError):
    return 0
