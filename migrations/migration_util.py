from types import ListType, TupleType

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