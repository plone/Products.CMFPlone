## Script (Python) "hasActionId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id
##title=checks the context for action id
##

try:
    action=context.getTypeInfo().getActionById(id)
    return 1
except:
    return 0

