## Script (Python) "getActionIconList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

from Products.CMFCore.utils import getToolByName

ai_tool = getToolByName(context, 'portal_actionicons')

class ActionIconInfo:
    pass

result = []
for ai in ai_tool.listActionIcons():
    info = ActionIconInfo()
    info.category = ai.getCategory()
    info.action = ai.getActionId()
    info.icon = ai.getIconURL()
    result.append(info)

return result
