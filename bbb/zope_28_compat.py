# An import that will fail unless we are using 2.8
from zope.component.servicenames import Presentation

from zope.component import queryMultiAdapter as queryMultiAdapter28
from zope.component import getMultiAdapter as getMultiAdapter28
from zope.component import queryView
from zope.interface import Interface

import zope.component

def queryMultiAdapter(objects, interface=Interface, name=u'', default=None,
                      context=None):
     """A monkey-patched queryMultiAdapter that falls back on view lookups"""
     adapted = queryMultiAdapter28(objects, interface, name=name,
                                   default=default, context=context)
     if adapted is None and len(objects)==2:
         adapted = queryView(objects[0], name, objects[1], default=default,
                             providing=interface, context=context)
     return adapted

def getMultiAdapter(objects, interface=Interface, name=u'', context=None):
    """A getMultiAdapter which doesn't require a provided interface"""
    return getMultiAdapter28(objects, interface=interface,
                             name=name, context=context)

if not hasattr(zope.component, '_queryMultiAdapter28'):
    zope.component.queryMultiAdapter = queryMultiAdapter
    zope.component.getMultiAdapter = getMultiAdapter
    zope.component._queryMultiAdapter28 = queryMultiAdapter28
    zope.component._getMultiAdapter28 = getMultiAdapter28