from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.SkinsTool import _populate

def setupSkinData(self):
    _populate(self)
    return 'fin'