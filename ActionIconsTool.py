from Products.CMFActionIcons.ActionIconsTool import ActionIconsTool as BaseTool
from Products.CMFActionIcons.permissions import View
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.PloneTool import _icons as iconcache

def removeAICacheEntry(category, id):
    if (category, id) in iconcache.keys():
        del iconcache[(category,id)]

class ActionIconsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.ActionIconsTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/confirm_icon.gif'

    security.declareProtected(View, 'renderActionIcon')
    def renderActionIcon( self,
                          category,
                          action_id,
                          default=None,
                          context=None ):
        """ Returns the actual object for the icon.  If you
            pass in a path elements in default it will attempt
            to traverse to that path.  Otherwise it will return
            None
        """
        icon = self.queryActionIcon( category,
                                     action_id,
                                     default=default,
                                     context=context )
        if icon is not None:
            portal=getToolByName(self, 'portal_url').getPortalObject()
            return portal.restrictedTraverse(icon)

        return default

    #Below we need to invalidate the cache for icons.  We have to
    #hardocde the module dict because we do not have events, yet.
    def updateActionIcon( self
                        , category
                        , action_id
                        , icon_expr
                        , title=None
                        , priority=0
                        ):
        """ update ActionIcons and remove cache entry """
        BaseTool.updateActionIcon(self, category, action_id, icon_expr,
                                  title, priority)
        removeAICacheEntry(category, action_id)

    def removeActionIcon( self, category, action_id ):
        """ remove ActionIcon and remove cache entry """
        BaseTool.removeActionIcon(self, category, action_id)
        removeAICacheEntry(category, action_id)

    def clearActionIcons( self ):
        """ clear ActionIcons and cache entries """
        BaseTool.clearActionIcons(self)
        iconcache.clear()

    def manage_updateActionIcon( self
                               , category
                               , action_id
                               , icon_expr
                               , title
                               , priority
                               , REQUEST
                               ):
        """ update ActionIcons from ZMI and remove cache entry """
        BaseTool.manage_updateActionIcon( self, category, action_id, icon_expr,
                                          title, priority, REQUEST )
        removeAICacheEntry(category, action_id)

    def manage_removeActionIcon( self, category, action_id, REQUEST ):
        """ remove ActionIcons from ZMI and remove cache entry """
        BaseTool.manage_removeActionIcon(self, category, action_id, REQUEST)
        removeAICacheEntry(category, action_id)

ActionIconsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionIconsTool)
