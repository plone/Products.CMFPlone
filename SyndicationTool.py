from Products.CMFDefault.SyndicationTool import SyndicationTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

actions = tuple(BaseTool._actions)
for a in actions:
    if a.id == 'syndication':
        a.visible = 0

class SyndicationTool(BaseTool):

    meta_type = ToolNames.SyndicationTool
    security = ClassSecurityInfo()
    _actions = actions

SyndicationTool.__doc__ = BaseTool.__doc__

InitializeClass(SyndicationTool)
