from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.SkinsTool import _upgrade

def upgrade(self):
    skinsTool = getToolByName(self, 'portal_skins')
    _upgrade(self, skinsTool)
    return 'fin'
    
    