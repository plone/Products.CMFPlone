from os import environ
from plone.memoize import forever


# Remember the installed products and packages (unless running tests)
if "ZOPETESTCASE" not in environ:
    from App import FactoryDispatcher

    FactoryDispatcher._product_packages = forever.memoize(
        FactoryDispatcher._product_packages
    )


# Avoid unneeded line breaks in TAL output, by effectively disabling the
# internal beautified wrapping inside tags
def wrap_init(func):
    def new_init(*args, **kwargs):
        kwargs["wrap"] = kwargs.get("wrap", 1023)
        func(*args, **kwargs)

    return new_init


from zope.tal.talinterpreter import TALInterpreter


TALInterpreter.__init__ = wrap_init(TALInterpreter.__init__)


# This is an optimization based on the fact,
# that opaque items are completely unused inside Plone
def opaqueItems(self):
    """
    Return opaque items (subelements that are contained
    using something that is not an ObjectManager).
    """
    return ()


from Products.CMFCore.CMFCatalogAware import OpaqueItemManager


OpaqueItemManager.opaqueItems = opaqueItems
