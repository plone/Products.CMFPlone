# 1. make sure allow_module can't be called from restricted code
import AccessControl
AccessControl.allow_module.__roles__ = ()

# 2. make sure /@@ doesn't traverse to annotations
from zope.traversing import namespace
from zope.traversing.interfaces import TraversalError
old_traverse = namespace.view.traverse
def traverse(self, name, ignored):
    if not name:
        raise TraversalError(self.context, name)
    return old_traverse(self, name, ignored)
namespace.view.traverse = traverse

# 3. be sure to check Access contents information permission for FTP users
from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from OFS.ObjectManager import ObjectManager
ObjectManager.__old_manage_FTPlist = ObjectManager.manage_FTPlist
def manage_FTPlist(self, REQUEST):
    """Returns a directory listing consisting of a tuple of
    (id,stat) tuples, marshaled to a string. Note, the listing it
    should include '..' if there is a Folder above the current
    one.

    In the case of non-foldoid objects it should return a single
    tuple (id,stat) representing itself."""

    if not getSecurityManager().checkPermission('Access contents information', self):
        raise Unauthorized('Not allowed to access contents.')

    return self.__old_manage_FTPlist(REQUEST)
ObjectManager.manage_FTPlist = manage_FTPlist

# 4. Make sure z3c.form widgets don't get declared as public
from Products.Five.metaconfigure import ClassDirective
old_require = ClassDirective.require
def require(self, *args, **kw):
    if self._ClassDirective__class.__module__.startswith('z3c.form.browser'):
        return
    return old_require(self, *args, **kw)
ClassDirective.require = require

# 5. Check return value of getToolByName
# This is an unusual sort of monkey patching...we replace just the func_code
# rather than the entire function, to make sure that aliases to the function
# that were imported prior to this patch will still run the patched code.
code = """
from persistent.interfaces import IPersistent
from OFS.interfaces import IItem
try:
    from Products.ATContentTypes.tool.factory import FauxArchetypeTool
except ImportError:
    FauxArchetypeTool = type('FauxArchetypeTool')

def _getToolByName(self, name, default=_marker):
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
        return result
    else:
        raise TypeError("Object found is not a portal tool (%s)" % (name,))
    return result
"""
from Products.CMFCore import utils
if '_marker' not in utils.getToolByName.func_globals:
    raise Exception("This Version of Products.CMFPlone is not compatible "
                    "with Products.PloneHotfix20121106, the fixes are "
                    "included already in Products.CMFPlone, please remove "
                    "the hotfix")
exec code in utils.getToolByName.func_globals
utils._getToolByName.func_code = utils.getToolByName.func_code
utils.getToolByName.func_code = utils.check_getToolByName.func_code

# 6. Protect some methods in ZCatalog
from Products.ZCatalog.ZCatalog import ZCatalog
ZCatalog.resolve_path__roles__ = ()
ZCatalog.resolve_url__roles__ = ()

# 7. Prevent publish traversal of the request
from ZPublisher.BaseRequest import BaseRequest
from ZPublisher.HTTPRequest import HTTPRequest
from zope.publisher.base import BaseRequest as ZPBaseRequest
from zope.publisher.ftp import FTPRequest
from zope.publisher.http import HTTPRequest as ZPHTTPRequest
for c in [BaseRequest, HTTPRequest, ZPBaseRequest, FTPRequest, ZPHTTPRequest]:
    try:
        del c.__doc__
    except:
        pass
