from types import ListType, TupleType
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
import zLOG

try:
    True
except NameError:
    True =1
    False=0

def safeEditProperty(obj, key, value, data_type='string'):
    """ An add or edit function, surprisingly useful :) """
    if obj.hasProperty(key):
        obj._updateProperty(key, value)
    else:
        obj._setProperty(key, value, data_type)

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
            # XXX that's bad :[
            return False, ('Can\'t convert actions of %s! Jumping to next action.' % actionprovider.getId(), zLOG.ERROR)
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