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
from Products.CMFPlone import bbb


if bbb.HAS_ZSERVER:
    from AccessControl import getSecurityManager
    from OFS.ObjectManager import ObjectManager
    from zExceptions import Unauthorized

    ObjectManager.__old_manage_FTPlist = ObjectManager.manage_FTPlist

    def manage_FTPlist(self, REQUEST):
        """Returns a directory listing consisting of a tuple of
        (id,stat) tuples, marshaled to a string. Note, the listing it
        should include '..' if there is a Folder above the current
        one.

        In the case of non-foldoid objects it should return a single
        tuple (id,stat) representing itself."""

        if not getSecurityManager().checkPermission(
            "Access contents information", self
        ):
            raise Unauthorized("Not allowed to access contents.")

        return self.__old_manage_FTPlist(REQUEST)

    ObjectManager.manage_FTPlist = manage_FTPlist

# 4. Make sure z3c.form widgets don't get declared as public
from AccessControl.metaconfigure import ClassDirective


old_require = ClassDirective.require


def require(self, *args, **kw):
    if self._ClassDirective__class.__module__.startswith("z3c.form.browser"):
        return
    return old_require(self, *args, **kw)


ClassDirective.require = require

# 5. Check return value of getToolByName
# Moved to patches/gtbn.py due to circular imports.

# 6. Protect some methods in ZCatalog
from Products.ZCatalog.ZCatalog import ZCatalog


ZCatalog.resolve_path__roles__ = ()
ZCatalog.resolve_url__roles__ = ()

from zope.publisher.base import BaseRequest as ZPBaseRequest
from zope.publisher.ftp import FTPRequest
from zope.publisher.http import HTTPRequest as ZPHTTPRequest

# 7. Prevent publish traversal of the request
from ZPublisher.BaseRequest import BaseRequest
from ZPublisher.HTTPRequest import HTTPRequest


for c in [BaseRequest, HTTPRequest, ZPBaseRequest, FTPRequest, ZPHTTPRequest]:
    try:
        del c.__doc__
    except Exception:
        pass
