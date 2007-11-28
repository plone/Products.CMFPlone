#
# Plone CatalogTool
#
import re
import time
import urllib

from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.CatalogTool import IndexableObjectWrapper

from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Globals import DTMLFile
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_base
from DateTime import DateTime
from BTrees.Length import Length

from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces.NonStructuralFolder import \
     INonStructuralFolder as z2INonStructuralFolder
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode
from OFS.IOrderSupport import IOrderedContainer
from ZODB.POSException import ConflictError

from Products.ZCatalog.ZCatalog import ZCatalog

from AccessControl.Permissions import manage_zcatalog_entries as ManageZCatalogEntries
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from AccessControl.PermissionRole import rolesForPermissionOn

from Products.CMFCore.interfaces import ISiteRoot

from zope.interface import Interface, implements, providedBy
from zope.component import adapts, getMultiAdapter

from plone.app.content.interfaces import IIndexableObjectWrapper

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


class ExtensibleIndexableObjectWrapper(IndexableObjectWrapper):
    """Extensible wrapper for object indexing.

    vars - additional vars as a dict, used for workflow vars like review_state
    obj - the indexable object
    portal - the portal root object
    registry - a registry
    **kwargs - additional keyword arguments
    """

    implements(IIndexableObjectWrapper)
    adapts(Interface, ISiteRoot)

    def __init__(self, obj, portal, registry = _eioRegistry):
        # Because we want to look this up as an adapter, we defer 
        # initialisation until the update() method is called
        super(ExtensibleIndexableObjectWrapper, self).__init__({}, obj)
        self._portal = portal
        self._registry = registry
        self._kwargs = {}

    def update(self, vars, **kwargs):
        self._IndexableObjectWrapper__vars = vars
        self._kwargs = kwargs
        if 'registry' in kwargs:
            self._registry = kwargs['registry']

    def beforeGetattrHook(self, vars, obj, kwargs):
        return vars, obj, kwargs

    def __getattr__(self, name):
        vars = self._IndexableObjectWrapper__vars
        obj = self._IndexableObjectWrapper__ob
        kwargs = self._kwargs
        registry = self._registry

        vars, obj, kwargs = self.beforeGetattrHook(vars, obj, kwargs)

        if registry.has_key(name):
            return registry[name](obj, portal=self._portal, vars=vars, **kwargs)
        return super(ExtensibleIndexableObjectWrapper, self).__getattr__(name)
    
    def allowedRolesAndUsers(self):
        # Disable CMFCore version of this method; use registry hook instead
        return self.__getattr__('allowedRolesAndUsers')


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


def object_provides(object, portal, **kw):
    return [i.__identifier__ for i in providedBy(object).flattened()]

registerIndexableAttribute('object_provides', object_provides)


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
    title = getattr(obj, 'Title', None)
    if title is not None:
        if safe_callable(title):
            title = title()
        if isinstance(title, basestring):
            sortabletitle = title.lower().strip()
            # Replace numbers with zero filled numbers
            sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
            # Truncate to prevent bloat
            sortabletitle = safe_unicode(sortabletitle)[:30].encode('utf-8')
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
    interfaces.

      >>> from Products.CMFPlone.CatalogTool import is_folderish
      >>> from Products.CMFPlone.interfaces import INonStructuralFolder
      >>> from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder as z2INonStructuralFolder
      >>> from zope.interface import directlyProvidedBy, directlyProvides

    A Folder is folderish generally::
      >>> is_folderish(self.folder)
      True

    But if we make it an INonStructuralFolder it is not::
      >>> base_implements = directlyProvidedBy(self.folder)
      >>> directlyProvides(self.folder, INonStructuralFolder, directlyProvidedBy(self.folder))
      >>> is_folderish(self.folder)
      False
      
    Now we revert our interface change and apply the z2 no-folderish interface::
      >>> directlyProvides(self.folder, base_implements)
      >>> is_folderish(self.folder)
      True
      >>> z2base_implements = self.folder.__implements__
      >>> self.folder.__implements__ = z2base_implements + (z2INonStructuralFolder,)
      >>> is_folderish(self.folder)
      False

    We again revert the interface change and check to make sure that
    PrincipiaFolderish is respected::
      >>> self.folder.__implements__ = z2base_implements
      >>> is_folderish(self.folder)
      True
      >>> self.folder.isPrincipiaFolderish = False
      >>> is_folderish(self.folder)
      False

    """
    # If the object explicitly states it doesn't want to be treated as a
    # structural folder, don't argue with it.
    folderish = bool(getattr(aq_base(obj), 'isPrincipiaFolderish', False))
    if not folderish:
        return False
    elif INonStructuralFolder.providedBy(obj):
        return False
    elif z2INonStructuralFolder.isImplementedBy(obj):
        # BBB: for z2 interface compat
        return False
    else:
        return folderish

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
    ptool = getToolByName(portal, 'plone_utils')
    return ptool.isDefaultPage(obj)

registerIndexableAttribute('is_default_page', is_default_page)


def getIcon(obj, **kwargs):
    """Make sure we index icon relative to portal"""
    return obj.getIcon(True)

registerIndexableAttribute('getIcon', getIcon)


class CatalogTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.CatalogTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/book_icon.gif'
    _counter = None

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
        self._increment_counter()
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
        
        w = getMultiAdapter((object, portal), IIndexableObjectWrapper)
        w.update(vars)
        
        ZCatalog.catalog_object(self, w, uid, idxs,
                                update_metadata, pghandler=pghandler)

    security.declareProtected(ManageZCatalogEntries, 'catalog_object')
    def uncatalog_object(self, *args, **kwargs):
        self._increment_counter()
        return BaseTool.uncatalog_object(self, *args, **kwargs)

    def _increment_counter(self):
        if self._counter is None:
            self._counter = Length()
        self._counter.change(1)

    security.declarePrivate('getCounter')
    def getCounter(self):
        return self._counter is not None and self._counter() or 0

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

    __call__ = searchResults

    security.declareProtected(ManageZCatalogEntries, 'clearFindAndRebuild')
    def clearFindAndRebuild(self):
        """Empties catalog, then finds all contentish objects (i.e. objects
           with an indexObject method), and reindexes them.
           This may take a long time.
        """
        def indexObject(obj, path):
            if (base_hasattr(obj, 'indexObject') and
                safe_callable(obj.indexObject)):
                try:
                    obj.indexObject()
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass
        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        portal.ZopeFindAndApply(portal, search_sub=True, apply_func=indexObject)

    security.declareProtected(ManageZCatalogEntries, 'manage_catalogRebuild')
    def manage_catalogRebuild(self, RESPONSE=None, URL1=None):
        """Clears the catalog and indexes all objects with an 'indexObject' method.
           This may take a long time.
        """
        elapse = time.time()
        c_elapse = time.clock()

        self.clearFindAndRebuild()

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse

        if RESPONSE is not None:
            RESPONSE.redirect(
              URL1 + '/manage_catalogAdvanced?manage_tabs_message=' +
              urllib.quote('Catalog Rebuilt\n'
                           'Total time: %s\n'
                           'Total CPU time: %s' % (`elapse`, `c_elapse`)))

CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
