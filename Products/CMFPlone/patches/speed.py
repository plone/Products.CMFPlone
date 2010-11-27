from plone.memoize import forever
from Acquisition import aq_base
from os import environ

# Remember the installed products and packages (unless running tests)
if not 'ZOPETESTCASE' in environ:
    from App import FactoryDispatcher
    FactoryDispatcher._product_packages = \
        forever.memoize(FactoryDispatcher._product_packages)

# Avoid unneeded line breaks in TAL output, by effectively disabling the
# internal beautified wrapping inside tags
def wrap_init(func):
    def new_init(*args, **kwargs):
        kwargs['wrap'] = kwargs.get('wrap', 1023)
        func(*args, **kwargs)
    return new_init

from zope.tal.talinterpreter import TALInterpreter
TALInterpreter.__init__ = wrap_init(TALInterpreter.__init__)

# This is an optimization based on the fact, that apart from talkback
# items, opaque items are completely unused inside Plone
def opaqueItems(self):
    """
        Return opaque items (subelements that are contained
        using something that is not an ObjectManager).
    """
    # Call 'talkback' knowing that it is an opaque item.
    # This will remain here as long as the discussion item does
    # not implement ICallableOpaqueItem (backwards compatibility).
    if hasattr(aq_base(self), 'talkback'):
        talkback = self.talkback
        if talkback is not None:
            return [(talkback.id, talkback)]
    return ()

from Products.CMFCore.CMFCatalogAware import OpaqueItemManager
OpaqueItemManager.opaqueItems = opaqueItems
