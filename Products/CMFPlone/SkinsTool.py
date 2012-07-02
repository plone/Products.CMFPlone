from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.SkinsTool import SkinsTool as BaseTool
from Products.ResourceRegistries.tools.BaseRegistry import \
    cookWhenChangingSettings

from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class SkinsTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Skins Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/skins_icon.png'

    default_skin = ''
    request_varname = 'plone_skin'

    security.declareProtected(ManagePortal, 'addSkinSelection')
    def addSkinSelection(self, skinname, skinpath, test=0, make_default=0):
        """ adds a skin selection 
        """
        super(SkinsTool, self).addSkinSelection(skinname, skinpath,
            test=test, make_default=make_default)
        # when adding a new skin, we need to tell RR about it
        cookWhenChangingSettings(None, None)

    security.declareProtected(ManagePortal, 'manage_skinLayers')
    def manage_skinLayers(self, chosen=(), add_skin=0, del_skin=0,
                          skinname='', skinpath='', REQUEST=None):
        """ Change the skinLayers.
        """
        response = super(SkinsTool, self).manage_skinLayers(chosen=chosen,
            add_skin=add_skin, del_skin=del_skin, skinname=skinname,
            skinpath=skinpath, REQUEST=REQUEST)
        # when changing skins, we need to tell RR about it
        cookWhenChangingSettings(None, None)
        return response

SkinsTool.__doc__ = BaseTool.__doc__

InitializeClass(SkinsTool)
