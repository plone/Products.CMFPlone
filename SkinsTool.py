from Products.CMFCore.SkinsTool import SkinsTool as BaseTool
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore import DirectoryView

_marker = []

# __getSkinByName can be renamed getSkinByName to 
# override SkinsContainer.getSkinByName.  This
# is about a 10% speed increase.

class SkinsTool(BaseTool):

    meta_type = ToolNames.SkinsTool
    security = ClassSecurityInfo()

    _v_skincache = {}

    security.declareProtected(ManagePortal, 'manage_skinLayers')
    def manage_skinLayers(self, chosen=(), add_skin=0, del_skin=0,
                          skinname='', skinpath='', REQUEST=None):
        BaseTool.manage_skinLayers(self, chosen, add_skin, del_skin, skinname, \
                                   skinpath, REQUEST)
        self.clearSkinCache()

    security.declareProtected(ManagePortal, 'manage_properties')
    def manage_properties(self, default_skin='', request_varname='',
                          allow_any=0, chosen=(), add_skin=0,
                          del_skin=0, skinname='', skinpath='',
                          cookie_persistence=0, REQUEST=None):
        BaseTool.manage_properties(self, defaul_skin, request_varname, \
                                   allow_any, chosen, add_skin, del_skin, \
                                   skinname, skinpath, cookie_persistence, \
                                   REQUEST)
        self.clearSkinCache()


    security.declareProtected(ManagePortal, 'addSkinSelection')
    def addSkinSelection(self, skinname, skinpath, test=0, make_default=0):
        BaseTool.addSkinSelection(self, skinname, skinpath, test, make_default)
        self.clearSkinCache()

    security.declarePrivate('getSkinByName')
    def getSkinByName(self, name):
        if getattr(self, '_v_skincache', None) is None:
            self.clearSkinCache()
        else:
            skinob = self._v_skincache.get(name, _marker)
            if skinob != _marker:
                return skinob
        path = self.getSkinPath(name)
        if path is None:
            skinob = None
        else:
            skinob = self.getSkinByPath(path)
        self._v_skincache[name] = skinob
        return skinob

    security.declareProtected(ManagePortal, 'clearSkinCache')
    def clearSkinCache(self):
        """force rebuilding the skin cache
        """
        self._v_skincache = {}

    security.declareProtected(ManagePortal, 'reloadSkinsFromFS')
    def reloadSkinsFromFS(self):
        """reload all files in the skin directories
        """
        self.clearSkinCache()
        for path in DirectoryView.manage_listAvailableDirectories():
            DirectoryView._dirreg.reloadDirectory(path)

SkinsTool.__doc__ = BaseTool.__doc__

InitializeClass(SkinsTool)


