# -*- coding: utf-8 -*-
from Products.CMFCore import utils

# Check return value of getToolByName
# this used to be step 5 in earlypatches, but was moved to avoid
# circular imports.
# This is an unusual sort of monkey patching...we replace just the func_code
# rather than the entire function, to make sure that aliases to the function
# that were imported prior to this patch will still run the patched code.
code = """
from Acquisition.interfaces import IAcquirer
from Acquisition import aq_base, aq_chain
from persistent.interfaces import IPersistent
from OFS.interfaces import IItem
from ZPublisher.BaseRequest import RequestContainer
try:
    from Products.ATContentTypes.tool.factory import FauxArchetypeTool
except ImportError:
    FauxArchetypeTool = type('FauxArchetypeTool')

def _getToolByName(obj, name, default=_marker):
    pass

def check_getToolByName(obj, name, default=_marker):
    result = _getToolByName(obj, name, default)
    if IPersistent.providedBy(result) or \
            IItem.providedBy(result) or \
            name in _tool_interface_registry or \
            (isinstance(result, FauxArchetypeTool)) or \
            '.test' in result.__class__.__module__ or \
            result.__class__.__module__ == 'mock' or \
            result is _marker or \
            result is default:
        # Rewrap in request container
        result_chain = aq_chain(result)
        obj_chain = aq_chain(obj)
        if (IAcquirer.providedBy(result) and
                not isinstance(result_chain[-1], RequestContainer) and
                isinstance(obj_chain[-1], RequestContainer)):
            result = obj_chain[-2]
            for ob in reversed(result_chain):
                result = aq_base(ob).__of__(result)
        return result
    else:
        raise TypeError("Object found is not a portal tool (%s)" % (name,))
    return result
"""
if '_marker' not in utils.getToolByName.func_globals:
    raise Exception("This Version of Products.CMFPlone is not compatible "
                    "with Products.PloneHotfix20121106, the fixes are "
                    "included already in Products.CMFPlone, please remove "
                    "the hotfix")
exec code in utils.getToolByName.func_globals
utils._getToolByName.func_code = utils.getToolByName.func_code
utils.getToolByName.func_code = utils.check_getToolByName.func_code
