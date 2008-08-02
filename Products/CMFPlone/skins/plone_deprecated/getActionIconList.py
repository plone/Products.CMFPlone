## Script (Python) "getActionIconList"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

context.plone_log("The getActionIconList script is deprecated and will be "
                  "removed in Plone 4.0.")

from Products.CMFCore.utils import getToolByName

ai_tool = getToolByName(context, 'portal_actionicons')
plone_utils = getToolByName(context, 'plone_utils')
normalizeString = plone_utils.normalizeString

class ActionIconInfo:
    pass

result = []
for ai in ai_tool.listActionIcons():
    info = ActionIconInfo()
    info.category = normalizeString(ai.getCategory())
    info.action = normalizeString(ai.getActionId())
    info.icon = ai.getIconURL()
    result.append(info)

return result
