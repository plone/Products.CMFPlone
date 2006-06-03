#
# Plone CatalogTool
#
import re
import urllib, time

from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import DTMLFile
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_base
from DateTime import DateTime

from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.interfaces.portal_catalog \
        import IndexableObjectWrapper as z2IIndexableObjectWrapper
from Products.CMFCore.interfaces import IIndexableObjectWrapper
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import log_deprecated
from OFS.IOrderSupport import IOrderedContainer
from ZODB.POSException import ConflictError

from Products.ZCatalog.ZCatalog import ZCatalog

from AccessControl.Permissions import manage_zcatalog_entries as ManageZCatalogEntries
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from AccessControl.PermissionRole import rolesForPermissionOn

from zope.interface import implements

_marker = object()


class ExtensibleIndexableObjectRegistry(dict):
    """Registry for extensible object indexing.
    """

    def register(self, name, callable):
        """Register a callable method for an attribute.

        The method will be called with the object as first argument and
        additional keyword arguments like portal and the workflow vars.
        """
        self[name] = callable

    def unregister(self, name):
        del self[name]

_eioRegistry = ExtensibleIndexableObjectRegistry()
registerIndexableAttribute = _eioRegistry.register


class ExtensibleIndexableObjectWrapper(object):
    """Extensible wrapper for object indexing.

    vars - additional vars as a dict, used for workflow vars like review_state
    obj - the indexable object
    portal - the portal root object
    registry - a registry
    **kwargs - additional keyword arguments
    """

    __implements__ = z2IIndexableObjectWrapper

    implements(IIndexableObjectWrapper)

    def __init__(self, vars, obj, portal, registry = _eioRegistry, **kwargs):
        self._vars = vars
        self._obj = obj
        self._portal = portal
        self._registry = registry
        self._kwargs = kwargs

    def beforeGetattrHook(self, vars, obj, kwargs):
        return vars, obj, kwargs

    def __getattr__(self, name):
        vars = self._vars
        obj = self._obj
        kwargs = self._kwargs
        registry = self._registry

        vars, obj, kwargs = self.beforeGetattrHook(vars, obj, kwargs)

        if registry.has_key(name):
            return registry[name](obj, portal=self._portal, vars=vars, **kwargs)
        if vars.has_key(name):
            return vars[name]
        return getattr(obj, name)


def allowedRolesAndUsers(obj, portal, **kwargs):
    """Return a list of roles and users with View permission.

    Used by PortalCatalog to filter out items you're not allowed to see.
    """
    allowed = {}
    for r in rolesForPermissionOn('View', obj):
        allowed[r] = 1
    try:
        localroles = portal.acl_users._getAllLocalRoles(obj)
    except AttributeError:
        localroles = _mergedLocalRoles(obj)
    for user, roles in localroles.items():
        for role in roles:
            if allowed.has_key(role):
                allowed['user:' + user] = 1
    if allowed.has_key('Owner'):
        del allowed['Owner']
    return list(allowed.keys())

registerIndexableAttribute('allowedRolesAndUsers', allowedRolesAndUsers)


def zero_fill(matchobj):
    return matchobj.group().zfill(8)

num_sort_regex = re.compile('\d+')


def sortable_title(obj, portal, **kwargs):
    """ Helper method for to provide FieldIndex for Title.

    >>> from Products.CMFPlone.CatalogTool import sortable_title

    >>> self.folder.setTitle('Plone42 _foo')
    >>> sortable_title(self.folder, self.portal)
    'plone00000042 _foo'
    """
    def_charset = portal.plone_utils.getSiteEncoding()
    title = getattr(obj, 'Title', None)
    if title is not None:
        if safe_callable(title):
            title = title()
        if isinstance(title, basestring):
            sortabletitle = title.lower().strip()
            # Replace numbers with zero filled numbers
            sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
            # Truncate to prevent bloat
            for charset in [def_charset, 'latin-1', 'utf-8']:
                try:
                    sortabletitle = unicode(sortabletitle, charset)[:30]
                    sortabletitle = sortabletitle.encode(def_charset or 'utf-8')
                    break
                except UnicodeError:
                    pass
                except TypeError:
                    # If we get a TypeError if we already have a unicode string
                    sortabletitle = sortabletitle[:30]
                    break
            return sortabletitle
    return ''

registerIndexableAttribute('sortable_title', sortable_title)


def getObjPositionInParent(obj, **kwargs):
    """ Helper method for catalog based folder contents.

    >>> from Products.CMFPlone.CatalogTool import getObjPositionInParent

    >>> getObjPositionInParent(self.folder)
    0
    """
    parent = aq_parent(aq_inner(obj))
    if IOrderedContainer.isImplementedBy(parent):
        try:
            return parent.getObjectPosition(obj.getId())
        except ConflictError:
            raise
        except:
            pass
            # XXX log
    return 0

registerIndexableAttribute('getObjPositionInParent', getObjPositionInParent)


SIZE_CONST = {'kB': 1024, 'MB': 1024*1024, 'GB': 1024*1024*1024}
SIZE_ORDER = ('GB', 'MB', 'kB')

def getObjSize(obj, **kwargs):
    """ Helper method for catalog based folder contents.

    >>> from Products.CMFPlone.CatalogTool import getObjSize

    >>> getObjSize(self.folder)
    '1 kB'
    """
    smaller = SIZE_ORDER[-1]

    if base_hasattr(obj, 'get_size'):
        size = obj.get_size()
    else:
        size = 0

    # if the size is a float, then make it an int
    # happens for large files
    try:
        size = int(size)
    except (ValueError, TypeError):
        pass

    if not size:
        return '0 %s' % smaller

    if isinstance(size, (int, long)):
        if size < SIZE_CONST[smaller]:
            return '1 %s' % smaller
        for c in SIZE_ORDER:
            if size/SIZE_CONST[c] > 0:
                break
        return '%.1f %s' % (float(size/float(SIZE_CONST[c])), c)
    return size

registerIndexableAttribute('getObjSize', getObjSize)


def is_folderish(obj, **kwargs):
    """Should this item be treated as a folder?

    Checks isPrincipiaFolderish, as well as the INonStructuralFolder
    interface.

    >>> from Products.CMFPlone.CatalogTool import is_folderish

    >>> is_folderish(self.folder)
    True
    """
    # If the object explicitly states it doesn't want to be treated as a
    # structural folder, don't argue with it.
    if INonStructuralFolder.providedBy(obj):
        return False
    else:
        return bool(getattr(aq_base(obj), 'isPrincipiaFolderish', False))

registerIndexableAttribute('is_folderish', is_folderish)


def syndication_enabled(obj, **kwargs):
    """Get state of syndication.
    """
    syn = getattr(aq_base(obj), 'syndication_information', _marker)
    if syn is not _marker:
        return True
    return False

registerIndexableAttribute('syndication_enabled', syndication_enabled)


def is_default_page(obj, portal, **kwargs):
    """Is this the default page in its folder
    """
    ptool = portal.plone_utils
    return ptool.isDefaultPage(obj)

registerIndexableAttribute('is_default_page', is_default_page)


class CatalogTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.CatalogTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/book_icon.gif'

    manage_catalogAdvanced = DTMLFile('www/catalogAdvanced', globals())

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__)

    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    def _removeIndex(self, index):
        """Safe removal of an index.
        """
        try:
            self.manage_delIndex(index)
        except:
            pass

    def _listAllowedRolesAndUsers(self, user):
        """Makes sure the list includes the user's groups.
        """
        result = list(user.getRoles())
        if hasattr(aq_base(user), 'getGroups'):
            result = result + ['user:%s' % x for x in user.getGroups()]
        result.append('Anonymous')
        result.append('user:%s' % user.getId())
        return result

    security.declarePrivate('indexObject')
    def indexObject(self, object, idxs=[]):
        """Add object to catalog.

        The optional idxs argument is a list of specific indexes
        to populate (all of them by default).
        """
        self.reindexObject(object, idxs)

    security.declareProtected(ManageZCatalogEntries, 'catalog_object')
    def catalog_object(self, object, uid, idxs=[],
                       update_metadata=1, pghandler=None):
        # Wraps the object with workflow and accessibility
        # information just before cataloging.
        wf = getattr(self, 'portal_workflow', None)
        # A comment for all the frustrated developers which aren't able to pin
        # point the code which adds the review_state to the catalog. :)
        # The review_state var and some other workflow vars are added to the
        # indexable object wrapper throught the code in the following lines
        if wf is not None:
            vars = wf.getCatalogVariablesFor(object)
        else:
            vars = {}
        portal = aq_parent(aq_inner(self))
        w = ExtensibleIndexableObjectWrapper(vars, object, portal=portal)
        ZCatalog.catalog_object(self, w, uid, idxs,
                                update_metadata, pghandler=pghandler)

    security.declareProtected(SearchZCatalog, 'searchResults')
    def searchResults(self, REQUEST=None, **kw):
        """Calls ZCatalog.searchResults with extra arguments that
        limit the results to what the user is allowed to see.

        This version uses the 'effectiveRange' DateRangeIndex.

        It also accepts a keyword argument show_inactive to disable
        effectiveRange checking entirely even for those without portal
        wide AccessInactivePortalContent permission.
        """
        kw = kw.copy()
        show_inactive = kw.get('show_inactive', False)

        user = _getAuthenticatedUser(self)
        kw['allowedRolesAndUsers'] = self._listAllowedRolesAndUsers(user)

        if not show_inactive and not _checkPermission(AccessInactivePortalContent, self):
            kw['effectiveRange'] = DateTime()

        return ZCatalog.searchResults(self, REQUEST, **kw)

    security.declareProtected(ManageZCatalogEntries, 'clearFindAndRebuild')
    def clearFindAndRebuild(self, REQUEST=None, RESPONSE=None, URL1=None):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with a reindexObject method), and reindexes them.
           This may take a long time."""

        elapse = time.time()
        c_elapse = time.clock()

        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(portal, search_sub=True,
                                apply_func=reindexContentObject)

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse

        if REQUEST and RESPONSE:
            RESPONSE.redirect(
                URL1 +
                '/manage_catalogAdvanced?manage_tabs_message=' +
                urllib.quote('Catalog Cleared and Recreated \n'
                             'Total time: %s\n'
                             'Total CPU time: %s' % (`elapse`, `c_elapse`)))

    __call__ = searchResults

CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)

# Utility function for calling reindexObject from ZopeFindAndApply
def reindexContentObject(obj, *args):
    """A method which reindexes an object if it is content.
       The ZopeFindAndApply method expects a function that takes both an
       object and a path as positional parameters."""
    if base_hasattr(obj, 'reindexObject') and \
            safe_callable(obj.reindexObject):
        try:
            obj.reindexObject()
        except TypeError:
            # Catalogs have this method as well, but they take
            # different args, and will fail
            pass
