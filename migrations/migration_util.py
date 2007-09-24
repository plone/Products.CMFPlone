from types import ListType, TupleType
from Acquisition import aq_base
import logging
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.MemberDataTool import MemberDataTool

from Products.PlonePAS.tools.memberdata \
        import MemberDataTool as PASMemberDataTool

_marker = []

def safeEditProperty(obj, key, value, data_type='string'):
    """ An add or edit function, surprisingly useful :) """
    if obj.hasProperty(key):
        obj._updateProperty(key, value)
    else:
        obj._setProperty(key, value, data_type)

def safeGetMemberDataTool(portal):
    memberdata = getToolByName(portal, 'portal_memberdata', None)
    if memberdata is not None:
        if memberdata.__class__ == MemberDataTool or \
                memberdata.__class__ == PASMemberDataTool:
            return memberdata

def addLinesToProperty(obj, key, values):
    if obj.hasProperty(key):
        data = getattr(obj, key)
        if type(data) is TupleType:
            data = list(data)
        if type(values) is ListType:
            data.extend(values)
        else:
            data.append(values)
        obj._updateProperty(key, data)
    else:
        if type(values) is not ListType:
            values = [values]
        obj._setProperty(key, values, 'lines')

def saveCloneActions(actionprovider):
    try:
        return True, actionprovider._cloneActions()
    except AttributeError:
        # Stumbled across ancient dictionary actions
        if not hasattr(aq_base(actionprovider), '_convertActions'):
            return False, ('Can\'t convert actions of %s! Jumping to next action.' % actionprovider.getId(), logging.ERROR)
        else:
            actionprovider._convertActions()
            return True, actionprovider._cloneActions()

def testSkinLayer(skinsTool, layer):
    """Make sure a skin layer exists"""
    # code adapted from CMFCore.SkinsContainer.getSkinByPath
    ob = aq_base(skinsTool)
    for name in layer.strip().split('/'):
        if not name:
            continue
        if name.startswith('_'):
            return 0
        ob = getattr(ob, name, None)
        if ob is None:
            return 0
    return 1

def cleanupSkinPath(portal, skinName, test=1):
   """Remove invalid skin layers from skins"""
   skinstool = getToolByName(portal, 'portal_skins')
   selections = skinstool._getSelections()
   old_path = selections[skinName].split(',')
   new_path = []
   for layer in old_path:
      if layer and testSkinLayer(skinstool, layer):
         new_path.append(layer)
   skinstool.addSkinSelection(skinName, ','.join(new_path), test=test)

def installOrReinstallProduct(portal, product_name, out, hidden=False):
    """Installs a product

    If product is already installed test if it needs to be reinstalled. Also
    fix skins after reinstalling
    """
    qi = getToolByName(portal, 'portal_quickinstaller')
    if not qi.isProductInstalled(product_name):
        qi.installProduct(product_name, hidden=hidden)
        # Refresh skins
        portal.clearCurrentSkin()
        portal.setupCurrentSkin(portal.REQUEST)
        out.append('Installed %s.' % product_name)
    else:
        info = qi._getOb(product_name)
        installed_version = info.getInstalledVersion()
        product_version = qi.getProductVersion(product_name)
        if installed_version != product_version:
            qi.reinstallProducts([product_name])
            out.append('%s is out of date (installed: %s/ filesystem: %s), '\
                'reinstalled.' % (product_name, installed_version, product_version))
        else:
            out.append('%s already installed.' % product_name)


def loadMigrationProfile(portal, profile, steps=_marker):
    tool = getToolByName(portal, "portal_setup")
    if steps is _marker:
        tool.runAllImportStepsFromProfile(profile, purge_old=False)
    else:
        for step in steps:
            tool.runImportStepFromProfile(profile,
                                          step,
                                          run_dependencies=False,
                                          purge_old=False)
