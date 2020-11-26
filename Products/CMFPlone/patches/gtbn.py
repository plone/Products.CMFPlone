from Acquisition import aq_parent, aq_base, aq_inner
from Acquisition import IAcquirer
from Products.CMFCore import utils
from zope.globalrequest import getRequest
from ZPublisher.BaseRequest import RequestContainer


def rewrap_in_request_container(obj, context=None):
    '''Fix an object's acquisition wrapper to be able to acquire the REQUEST.'''
    request = getattr(context, 'REQUEST', None) or getRequest()
    if IAcquirer.providedBy(obj) and request is not None:
        chain = []
        parent = obj
        while 1:
            chain.append(parent)
            parent = aq_parent(aq_inner(parent))
            if parent in chain or parent is None or isinstance(
                    parent, RequestContainer):
                break
        obj = RequestContainer(REQUEST=request)
        for ob in reversed(chain):
            obj = aq_base(ob).__of__(obj)
    return obj

# Check return value of getToolByName
# this used to be step 5 in earlypatches, but was moved to avoid
# circular imports.
# This is an unusual sort of monkey patching...we replace just the func_code
# rather than the entire function, to make sure that aliases to the function
# that were imported prior to this patch will still run the patched code.
code = """
from persistent.interfaces import IPersistent
from OFS.interfaces import IItem

def _getToolByName(obj, name, default=_marker):
    pass

def check_getToolByName(obj, name, default=_marker):
    result = _getToolByName(obj, name, default)
    if IPersistent.providedBy(result) or \
            IItem.providedBy(result) or \
            name in _tool_interface_registry or \
            '.test' in result.__class__.__module__ or \
            result.__class__.__module__ == 'mock' or \
            result is _marker or \
            result is default:
        return rewrap_in_request_container(result, context=obj)
    else:
        raise TypeError("Object found is not a portal tool (%s)" % (name,))
    return result
"""
if '_marker' not in utils.getToolByName.__globals__:
    raise Exception("This Version of Products.CMFPlone is not compatible "
                    "with Products.PloneHotfix20121106, the fixes are "
                    "included already in Products.CMFPlone, please remove "
                    "the hotfix")
utils.getToolByName.__globals__[
    'rewrap_in_request_container'] = rewrap_in_request_container
exec(code, utils.getToolByName.__globals__)
utils._getToolByName.__code__ = utils.getToolByName.__code__
utils.getToolByName.__code__ = utils.check_getToolByName.__code__
