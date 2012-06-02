from Products.CMFActionIcons.ActionIconsTool import ActionIconsTool as BaseTool
from Products.CMFActionIcons.permissions import View
from Products.CMFCore.utils import getToolByName
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.PloneTool import _icons as iconcache
from Products.CMFPlone.log import log_deprecated


WHITELISTED_AI = set([
    'controlpanel/ImagingSettings',
    'controlpanel/tinymce',
    'controlpanel/versioning',
])


def removeAICacheEntry(category, id):
    if (category, id) in iconcache.keys():
        del iconcache[(category, id)]


class ActionIconsTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Action Icons Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/confirm_icon.png'

    security.declareProtected(View, 'renderActionIcon')
    def renderActionIcon(self,
                         category,
                         action_id,
                         default=None,
                         context=None):
        """ Returns the actual object for the icon.  If you
            pass in a path elements in default it will attempt
            to traverse to that path.  Otherwise it will return
            None
        """
        icon = self.queryActionIcon(category,
                                    action_id,
                                    default=default,
                                    context=context)
        if icon is not None:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            return portal.restrictedTraverse(icon)

        return default

    def getActionIcon(self, category, action_id, context=None):
        ai = BaseTool.getActionIcon(self, category, action_id,
                                    context=context)
        if ai:
            log_deprecated("The icon for the '%s/%s' action was obtained from "
                           "the action icons tool. The action icons tool has "
                           "been deprecated and will be removed in Plone 5. "
                           "You should register action icons directly on the "
                           "action now, using the 'icon_expr' "
                           "setting." % (category, action_id))
            return ai
        return None

    def queryActionIcon(self, category, action_id, default=None, context=None):
        ai = BaseTool.queryActionIcon(self, category, action_id,
                                      default=default, context=context)
        if ai:
            log_deprecated("The icon for the '%s/%s' action was obtained from "
                           "the action icons tool. The action icons tool has "
                           "been deprecated and will be removed in Plone 5. "
                           "You should register action icons directly on the "
                           "action now, using the 'icon_expr' "
                           "setting." % (category, action_id))
            return ai
        return None

    def addActionIcon(self, category, action_id, icon_expr, title=None,
                      priority=0):
        combination = '%s/%s' % (category, action_id)
        if combination not in WHITELISTED_AI:
            log_deprecated("An icon for the '%s' action is being added to "
                           "the action icons tool. The action icons tool has "
                           "been deprecated and will be removed in Plone 5. "
                           "You should register action icons directly on the "
                           "action now, using the 'icon_expr' "
                           "setting." % combination)
        return BaseTool.addActionIcon(self, category, action_id, icon_expr,
                                      title, priority)

    #Below we need to invalidate the cache for icons.  We have to
    #hardocde the module dict because we do not have events, yet.
    def updateActionIcon(self, category, action_id, icon_expr,
                         title=None, priority=0):
        """ update ActionIcons and remove cache entry """
        log_deprecated("The icon for the '%s/%s' action is being updated on "
                       "the action icons tool. The action icons tool has "
                       "been deprecated and will be removed in Plone 5. "
                       "You should register action icons directly on the "
                       "action now, using the 'icon_expr' "
                       "setting." % (category, action_id))
        BaseTool.updateActionIcon(self, category, action_id, icon_expr,
                                  title, priority)
        removeAICacheEntry(category, action_id)

    def removeActionIcon(self, category, action_id):
        """ remove ActionIcon and remove cache entry """
        BaseTool.removeActionIcon(self, category, action_id)
        removeAICacheEntry(category, action_id)

    def clearActionIcons(self):
        """ clear ActionIcons and cache entries """
        BaseTool.clearActionIcons(self)
        iconcache.clear()

    def manage_updateActionIcon(self, category, action_id, icon_expr, title,
                                priority, REQUEST):
        """ update ActionIcons from ZMI and remove cache entry """
        BaseTool.manage_updateActionIcon(self, category, action_id, icon_expr,
                                         title, priority, REQUEST)
        removeAICacheEntry(category, action_id)

    def manage_removeActionIcon(self, category, action_id, REQUEST):
        """ remove ActionIcons from ZMI and remove cache entry """
        BaseTool.manage_removeActionIcon(self, category, action_id, REQUEST)
        removeAICacheEntry(category, action_id)

ActionIconsTool.__doc__ = BaseTool.__doc__

InitializeClass(ActionIconsTool)
