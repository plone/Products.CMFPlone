from Products.CMFDefault.SyndicationTool import SyndicationTool as BaseTool
from Products.CMFPlone import ToolNames
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import ManageProperties
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo, Unauthorized
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

actions = tuple(BaseTool._actions)
for a in actions:
    if a.id == 'syndication':
        a.condition=Expression(text='python: folder is object and portal.portal_syndication.isSiteSyndicationAllowed()')

class SyndicationTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.SyndicationTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/rss.gif'
    _actions = actions

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    security.declarePublic('getSyndicatableContent')
    def getSyndicatableContent(self, obj):
        """ Use the getFolderContents script, unless
        an object (like Topic) overrides it
        """
        # should we be doing aq_base here?
        if hasattr(obj, 'synContentValues'):
            values = obj.synContentValues()
        else:
            values = obj.getFolderContents()
        return values

    # Add protection to these methods to allow only appropriate users
    # to set syndication properties
    def enableSyndication(self, obj):
        """
        Enable syndication for the obj
        """
        mtool = getToolByName(self, 'portal_membership')
        if not mtool.checkPermission(ManageProperties, obj):
            raise Unauthorized
        BaseTool.enableSyndication(self, obj)

    def disableSyndication(self, obj):
        """
        Disable syndication for the obj; and remove it.
        """
        mtool = getToolByName(self, 'portal_membership')
        if not mtool.checkPermission(ManageProperties, obj):
            raise Unauthorized
        BaseTool.disableSyndication(self, obj)

SyndicationTool.__doc__ = BaseTool.__doc__

InitializeClass(SyndicationTool)
