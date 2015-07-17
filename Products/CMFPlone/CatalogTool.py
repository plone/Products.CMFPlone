import logging
import re
import time
import urllib

from AccessControl import ClassSecurityInfo
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permissions import (
    manage_zcatalog_entries as ManageZCatalogEntries)
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from BTrees.Length import Length
from DateTime import DateTime
from OFS.interfaces import IOrderedContainer
from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces import IPloneCatalogTool
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_unicode
from Products.ZCatalog.ZCatalog import ZCatalog
from plone.i18n.normalizer.base import mapUnicode
from plone.indexer import indexer
from plone.indexer.interfaces import IIndexableObject
from zope.component import queryMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from zope.interface import providedBy


logger = logging.getLogger('Plone')

_marker = object()

MAX_SORTABLE_TITLE = 40
BLACKLISTED_INTERFACES = frozenset((
    'AccessControl.interfaces.IOwned',
    'AccessControl.interfaces.IPermissionMappingSupport',
    'AccessControl.interfaces.IRoleManager',
    'Acquisition.interfaces.IAcquirer',
    'App.interfaces.INavigation',
    'App.interfaces.IPersistentExtra',
    'App.interfaces.IUndoSupport',
    'archetypes.schemaextender.interfaces.IExtensible',
    'OFS.interfaces.ICopyContainer',
    'OFS.interfaces.ICopySource',
    'OFS.interfaces.IFindSupport',
    'OFS.interfaces.IFolder',
    'OFS.interfaces.IFTPAccess',
    'OFS.interfaces.IItem',
    'OFS.interfaces.IManageable',
    'OFS.interfaces.IObjectManager',
    'OFS.interfaces.IOrderedContainer',
    'OFS.interfaces.IPropertyManager',
    'OFS.interfaces.ISimpleItem',
    'OFS.interfaces.ITraversable',
    'OFS.interfaces.IZopeObject',
    'persistent.interfaces.IPersistent',
    'plone.app.folder.bbb.IArchivable',
    'plone.app.folder.bbb.IPhotoAlbumAble',
    'plone.app.folder.folder.IATUnifiedFolder',
    'plone.app.imaging.interfaces.IBaseObject',
    'plone.app.iterate.interfaces.IIterateAware',
    'plone.app.kss.interfaces.IPortalObject',
    'plone.contentrules.engine.interfaces.IRuleAssignable',
    'plone.folder.interfaces.IFolder',
    'plone.folder.interfaces.IOrderableFolder',
    'plone.locking.interfaces.ITTWLockable',
    'plone.portlets.interfaces.ILocalPortletAssignable',
    'plone.uuid.interfaces.IUUIDAware',
    'Products.Archetypes.interfaces.athistoryaware.IATHistoryAware',
    'Products.Archetypes.interfaces.base.IBaseContent',
    'Products.Archetypes.interfaces.base.IBaseFolder',
    'Products.Archetypes.interfaces.base.IBaseObject',
    'Products.Archetypes.interfaces.metadata.IExtensibleMetadata',
    'Products.Archetypes.interfaces.referenceable.IReferenceable',
    'Products.ATContentTypes.exportimport.content.IDisabledExport',
    'Products.ATContentTypes.interfaces.folder.IATBTreeFolder',
    'Products.ATContentTypes.interfaces.interfaces.IATContentType',
    'Products.ATContentTypes.interfaces.interfaces.IHistoryAware',
    'Products.ATContentTypes.interfaces.interfaces.ITextContent',
    'Products.CMFCore.interfaces._content.ICatalogableDublinCore',
    'Products.CMFCore.interfaces._content.ICatalogAware',
    'Products.CMFCore.interfaces._content.IDublinCore',
    'Products.CMFCore.interfaces._content.IDynamicType',
    'Products.CMFCore.interfaces._content.IFolderish',
    'Products.CMFCore.interfaces._content.IMinimalDublinCore',
    'Products.CMFCore.interfaces._content.IMutableDublinCore',
    'Products.CMFCore.interfaces._content.IMutableMinimalDublinCore',
    'Products.CMFCore.interfaces._content.IOpaqueItemManager',
    'Products.CMFCore.interfaces._content.IWorkflowAware',
    'Products.CMFDynamicViewFTI.interfaces.IBrowserDefault',
    'Products.CMFDynamicViewFTI.interfaces.ISelectableBrowserDefault',
    'Products.CMFPlone.interfaces.constrains.IConstrainTypes',
    'Products.CMFPlone.interfaces.constrains.ISelectableConstrainTypes',
    'Products.GenericSetup.interfaces.IDAVAware',
    'webdav.EtagSupport.EtagBaseInterface',
    'webdav.interfaces.IDAVCollection',
    'webdav.interfaces.IDAVResource',
    'zope.annotation.interfaces.IAnnotatable',
    'zope.annotation.interfaces.IAttributeAnnotatable',
    'zope.component.interfaces.IPossibleSite',
    'zope.container.interfaces.IContainer',
    'zope.container.interfaces.IItemContainer',
    'zope.container.interfaces.IReadContainer',
    'zope.container.interfaces.ISimpleReadContainer',
    'zope.container.interfaces.IWriteContainer',
    'zope.interface.common.mapping.IEnumerableMapping',
    'zope.interface.common.mapping.IItemMapping',
    'zope.interface.common.mapping.IReadMapping',
    'zope.interface.Interface',
))


@indexer(Interface)
def allowedRolesAndUsers(obj):
    """Return a list of roles and users with View permission.
    Used to filter out items you're not allowed to see.
    """
    allowed = set(rolesForPermissionOn('View', obj))
    # shortcut roles and only index the most basic system role if the object
    # is viewable by either of those
    if 'Anonymous' in allowed:
        return ['Anonymous']
    elif 'Authenticated' in allowed:
        return ['Authenticated']
    localroles = {}
    try:
        acl_users = getToolByName(obj, 'acl_users', None)
        if acl_users is not None:
            localroles = acl_users._getAllLocalRoles(obj)
    except AttributeError:
        localroles = _mergedLocalRoles(obj)
    for user, roles in localroles.items():
        if allowed.intersection(roles):
            allowed.update(['user:' + user])
    if 'Owner' in allowed:
        allowed.remove('Owner')
    return list(allowed)


@indexer(Interface)
def object_provides(obj):
    return tuple(
        [i.__identifier__ for i in providedBy(obj).flattened()
         if i.__identifier__ not in BLACKLISTED_INTERFACES]
    )


def zero_fill(matchobj):
    return matchobj.group().zfill(4)

num_sort_regex = re.compile('\d+')


@indexer(Interface)
def sortable_title(obj):
    """ Helper method for to provide FieldIndex for Title.
    """
    title = getattr(obj, 'Title', None)
    if title is not None:
        if safe_callable(title):
            title = title()

        if isinstance(title, basestring):
            # Ignore case, normalize accents, strip spaces
            sortabletitle = mapUnicode(safe_unicode(title)).lower().strip()
            # Replace numbers with zero filled numbers
            sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
            # Truncate to prevent bloat, take bits from start and end
            if len(sortabletitle) > MAX_SORTABLE_TITLE:
                start = sortabletitle[:(MAX_SORTABLE_TITLE - 13)]
                end = sortabletitle[-10:]
                sortabletitle = start + '...' + end
            return sortabletitle.encode('utf-8')
    return ''


@indexer(Interface)
def getObjPositionInParent(obj):
    """ Helper method for catalog based folder contents.
    """
    parent = aq_parent(aq_inner(obj))
    ordered = IOrderedContainer(parent, None)
    if ordered is not None:
        return ordered.getObjectPosition(obj.getId())
    return 0

SIZE_CONST = {'KB': 1024, 'MB': 1024 * 1024, 'GB': 1024 * 1024 * 1024}
SIZE_ORDER = ('GB', 'MB', 'KB')


@indexer(Interface)
def getObjSize(obj):
    """ Helper method for catalog based folder contents.
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
            if size / SIZE_CONST[c] > 0:
                break
        return '%.1f %s' % (float(size / float(SIZE_CONST[c])), c)
    return size


@indexer(Interface)
def is_folderish(obj):
    """Should this item be treated as a folder?

    Checks isPrincipiaFolderish, as well as the INonStructuralFolder
    interfaces.
    """
    # If the object explicitly states it doesn't want to be treated as a
    # structural folder, don't argue with it.
    folderish = bool(getattr(aq_base(obj), 'isPrincipiaFolderish', False))
    return folderish and not INonStructuralFolder.providedBy(obj)


@indexer(Interface)
def is_default_page(obj):
    """Is this the default page in its folder
    """
    ptool = getToolByName(obj, 'plone_utils', None)
    if ptool is None:
        return False
    return ptool.isDefaultPage(obj)


@indexer(Interface)
def getIcon(obj):
    """Make sure we index icon relative to portal"""
    return obj.getIcon(True)


@indexer(Interface)
def location(obj):
    return obj.getField('location').get(obj)


@implementer(IPloneCatalogTool)
class CatalogTool(PloneBaseTool, BaseTool):
    """Plone's catalog tool"""

    meta_type = 'Plone Catalog Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/book_icon.png'
    _counter = None

    manage_catalogAdvanced = DTMLFile('www/catalogAdvanced', globals())

    manage_options = (
        {'action': 'manage_main', 'label': 'Contents'},
        {'action': 'manage_catalogView', 'label': 'Catalog'},
        {'action': 'manage_catalogIndexes', 'label': 'Indexes'},
        {'action': 'manage_catalogSchema', 'label': 'Metadata'},
        {'action': 'manage_catalogAdvanced', 'label': 'Advanced'},
        {'action': 'manage_catalogReport', 'label': 'Query Report'},
        {'action': 'manage_catalogPlan', 'label': 'Query Plan'},
        {'action': 'manage_propertiesForm', 'label': 'Properties'},
    )

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
        result = user.getRoles()
        if 'Anonymous' in result:
            # The anonymous user has no further roles
            return ['Anonymous']
        result = list(result)
        if hasattr(aq_base(user), 'getGroups'):
            groups = ['user:%s' % x for x in user.getGroups()]
            if groups:
                result = result + groups
        # Order the arguments from small to large sets
        result.insert(0, 'user:%s' % user.getId())
        result.append('Anonymous')
        return result

    @security.private
    def indexObject(self, object, idxs=None):
        """Add object to catalog.

        The optional idxs argument is a list of specific indexes
        to populate (all of them by default).
        """
        if idxs is None:
            idxs = []
        self.reindexObject(object, idxs)

    @security.protected(ManageZCatalogEntries)
    def catalog_object(self, object, uid=None, idxs=None,
                       update_metadata=1, pghandler=None):
        if idxs is None:
            idxs = []
        self._increment_counter()

        w = object
        if not IIndexableObject.providedBy(object):
            # This is the CMF 2.2 compatible approach, which should be used
            # going forward
            wrapper = queryMultiAdapter((object, self), IIndexableObject)
            if wrapper is not None:
                w = wrapper

        ZCatalog.catalog_object(self, w, uid, idxs,
                                update_metadata, pghandler=pghandler)

    @security.protected(ManageZCatalogEntries)
    def uncatalog_object(self, *args, **kwargs):
        self._increment_counter()
        return BaseTool.uncatalog_object(self, *args, **kwargs)

    def _increment_counter(self):
        if self._counter is None:
            self._counter = Length()
        self._counter.change(1)

    @security.private
    def getCounter(self):
        return self._counter is not None and self._counter() or 0

    @security.protected(SearchZCatalog)
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
        if isinstance(REQUEST, dict) and not show_inactive:
            show_inactive = 'show_inactive' in REQUEST

        user = _getAuthenticatedUser(self)
        kw['allowedRolesAndUsers'] = self._listAllowedRolesAndUsers(user)

        if not show_inactive \
           and not _checkPermission(AccessInactivePortalContent, self):
            kw['effectiveRange'] = DateTime()

        return ZCatalog.searchResults(self, REQUEST, **kw)

    __call__ = searchResults

    def search(self, *args, **kw):
        # Wrap search() the same way that searchResults() is
        query = {}

        if args:
            query = args[0]
        elif 'query_request' in kw:
            query = kw.get('query_request')

        kw['query_request'] = query.copy()

        user = _getAuthenticatedUser(self)
        query['allowedRolesAndUsers'] = self._listAllowedRolesAndUsers(user)

        if not _checkPermission(AccessInactivePortalContent, self):
            query['effectiveRange'] = DateTime()

        kw['query_request'] = query

        return super(CatalogTool, self).search(**kw)

    @security.protected(ManageZCatalogEntries)
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
        portal.ZopeFindAndApply(
            portal,
            search_sub=True,
            apply_func=indexObject
        )

    @security.protected(ManageZCatalogEntries)
    def manage_catalogRebuild(self, RESPONSE=None, URL1=None):
        """Clears the catalog and indexes all objects with an 'indexObject'
        method. This may take a long time.
        """
        elapse = time.time()
        c_elapse = time.clock()

        self.clearFindAndRebuild()

        elapse = time.time() - elapse
        c_elapse = time.clock() - c_elapse

        msg = ('Catalog Rebuilt\n'
               'Total time: %s\n'
               'Total CPU time: %s' % (repr(elapse), repr(c_elapse)))
        logger.info(msg)

        if RESPONSE is not None:
            RESPONSE.redirect(
                URL1 + '/manage_catalogAdvanced?manage_tabs_message=' +
                urllib.quote(msg))

InitializeClass(CatalogTool)
