from types import ListType, TupleType
from Acquisition import aq_base
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
