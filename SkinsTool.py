from Products.CMFCore.SkinsTool import SkinsTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore import DirectoryView

_skincache = {}

# __getSkinByName can be renamed getSkinByName to 
# override SkinsContainer.getSkinByName.  This
# is about a 10% speed increase.

class SkinsTool(BaseTool):

    meta_type = ToolNames.SkinsTool
    security = ClassSecurityInfo()

    security.declarePrivate('getSkinByName')
    def __getSkinByName(self, name):
        path = self.getSkinPath(name)
        if path is None:
            return None
        if path not in _skincache.keys():
            _skincache[path]=None
        if _skincache[path]:
            return _skincache[path]
        skinob=self.getSkinByPath(path)
        _skincache[path]=skinob
        return skinob
 
SkinsTool.__doc__ = BaseTool.__doc__

InitializeClass(SkinsTool)
