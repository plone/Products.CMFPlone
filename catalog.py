from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from zope.app.component.interface import interfaceToName
from zope.app.apidoc.component import getRequiredAdapters
from zope.interface import providedBy

# Use extensible object wrapper to always list the interfaces
def object_implements(object, portal, **kw):
    return [interfaceToName(portal, i) for i in providedBy(object).flattened()]

registerIndexableAttribute('object_implements', object_implements)


def object_adapts_to(object, portal, **kw):
    res = {}

    for iface in providedBy(object).flattened():
        res[interfaceToName(portal, iface)] = iface

    direct = res.values()
    for iface in direct:
        for adapter_reg in getRequiredAdapters(iface):
            adaptable_iface = adapter_reg.provided
            adapting_from = [i for i in adapter_reg.required
                             if i is not None]
            skip = False
            if len(adapting_from) > 1:
                # only support multiadapters that this object can satisfy alone
                for i in adapting_from:
                    if not i in direct:
                        skip = True
            if adaptable_iface is not None and not skip:
                res[interfaceToName(portal, adaptable_iface)] = adaptable_iface

    return res.keys()


registerIndexableAttribute('object_adapts_to', object_adapts_to)

