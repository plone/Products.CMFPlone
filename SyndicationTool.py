from Products.CMFDefault.SyndicationTool import SyndicationTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.CMFCore.Expression import Expression
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

actions = tuple(BaseTool._actions)
for a in actions:
    if a.id == 'syndication':
        a.condition=Expression(text='python: folder is object and portal.portal_syndication.isSiteSyndicationAllowed()')

class SyndicationTool(BaseTool):

    meta_type = ToolNames.SyndicationTool
    security = ClassSecurityInfo()
    _actions = actions

SyndicationTool.__doc__ = BaseTool.__doc__

InitializeClass(SyndicationTool)
