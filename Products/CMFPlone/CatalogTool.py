from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.Permissions import manage_zcatalog_entries as ManageZCatalogEntries
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.special_dtml import DTMLFile
from BTrees.Length import Length
from DateTime import DateTime
from OFS.interfaces import IOrderedContainer
from plone.app.discussion.interfaces import DISCUSSION_ANNOTATION_KEY
from plone.base.interfaces import INonStructuralFolder
from plone.base.interfaces import IPloneCatalogTool
from plone.base.utils import base_hasattr
from plone.base.utils import human_readable_size
from plone.base.utils import safe_callable
from plone.base.utils import safe_text
from plone.i18n.normalizer.base import mapUnicode
from plone.indexer import indexer
from plone.indexer.interfaces import IIndexableObject
from plone.namedfile.interfaces import IImage
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.indexing import processQueue
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.ZCatalog.ZCatalog import ZCatalog
from time import process_time
from zExceptions import Unauthorized
from zope.annotation.interfaces import IAnnotations
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import providedBy

import logging
import re
import time
import urllib


logger = logging.getLogger("Plone")

_marker = object()

DENIED_INTERFACES = frozenset(
    (
        "AccessControl.interfaces.IOwned",
        "AccessControl.interfaces.IPermissionMappingSupport",
        "AccessControl.interfaces.IRoleManager",
        "Acquisition.interfaces.IAcquirer",
        "App.interfaces.INavigation",
        "App.interfaces.IPersistentExtra",
        "App.interfaces.IUndoSupport",
        "OFS.interfaces.ICopyContainer",
        "OFS.interfaces.ICopySource",
        "OFS.interfaces.IFindSupport",
        "OFS.interfaces.IFolder",
        "OFS.interfaces.IFTPAccess",
        "OFS.interfaces.IItem",
        "OFS.interfaces.IManageable",
        "OFS.interfaces.IObjectManager",
        "OFS.interfaces.IOrderedContainer",
        "OFS.interfaces.IPropertyManager",
        "OFS.interfaces.ISimpleItem",
        "OFS.interfaces.ITraversable",
        "OFS.interfaces.IZopeObject",
        "persistent.interfaces.IPersistent",
        "plone.app.iterate.interfaces.IIterateAware",
        "plone.contentrules.engine.interfaces.IRuleAssignable",
        "plone.folder.interfaces.IFolder",
        "plone.folder.interfaces.IOrderableFolder",
        "plone.locking.interfaces.ITTWLockable",
        "plone.portlets.interfaces.ILocalPortletAssignable",
        "plone.uuid.interfaces.IUUIDAware",
        "Products.CMFCore.interfaces._content.ICatalogableDublinCore",
        "Products.CMFCore.interfaces._content.ICatalogAware",
        "Products.CMFCore.interfaces._content.IDublinCore",
        "Products.CMFCore.interfaces._content.IDynamicType",
        "Products.CMFCore.interfaces._content.IFolderish",
        "Products.CMFCore.interfaces._content.IMinimalDublinCore",
        "Products.CMFCore.interfaces._content.IMutableDublinCore",
        "Products.CMFCore.interfaces._content.IMutableMinimalDublinCore",
        "Products.CMFCore.interfaces._content.IOpaqueItemManager",
        "Products.CMFCore.interfaces._content.IWorkflowAware",
        "Products.CMFDynamicViewFTI.interfaces.IBrowserDefault",
        "Products.CMFDynamicViewFTI.interfaces.ISelectableBrowserDefault",
        "plone.base.interfaces.constrains.IConstrainTypes",
        "plone.base.interfaces.constrains.ISelectableConstrainTypes",
        "Products.GenericSetup.interfaces.IDAVAware",
        "webdav.EtagSupport.EtagBaseInterface",
        "webdav.interfaces.IDAVCollection",
        "webdav.interfaces.IDAVResource",
        "zope.annotation.interfaces.IAnnotatable",
        "zope.annotation.interfaces.IAttributeAnnotatable",
        "zope.component.interfaces.IPossibleSite",
        "zope.container.interfaces.IContainer",
        "zope.container.interfaces.IItemContainer",
        "zope.container.interfaces.IReadContainer",
        "zope.container.interfaces.ISimpleReadContainer",
        "zope.container.interfaces.IWriteContainer",
        "zope.interface.common.mapping.IEnumerableMapping",
        "zope.interface.common.mapping.IItemMapping",
        "zope.interface.common.mapping.IReadMapping",
        "zope.interface.Interface",
    )
)

# bbb, remove in Plone 7
BLACKLISTED_INTERFACES = DENIED_INTERFACES


@indexer(Interface)
def allowedRolesAndUsers(obj):
    """Return a list of roles and users with View permission.
    Used to filter out items you're not allowed to see.
    """

    # 'Access contents information' is the correct permission for
    # accessing and displaying metadata of an item.
    # 'View' should be reserved for accessing the item itself.
    allowed = set(rolesForPermissionOn("Access contents information", obj))

    # shortcut roles and only index the most basic system role if the object
    # is viewable by either of those
    if "Anonymous" in allowed:
        return ["Anonymous"]
    elif "Authenticated" in allowed:
        return ["Authenticated"]
    localroles = {}
    try:
        acl_users = getToolByName(obj, "acl_users", None)
        if acl_users is not None:
            localroles = acl_users._getAllLocalRoles(obj)
    except AttributeError:
        localroles = _mergedLocalRoles(obj)
    for user, roles in localroles.items():
        if allowed.intersection(roles):
            allowed.update(["user:" + user])
    if "Owner" in allowed:
        allowed.remove("Owner")
    return list(allowed)


@indexer(Interface)
def object_provides(obj):
    return tuple(
        i.__identifier__
        for i in providedBy(obj).flattened()
        if i.__identifier__ not in DENIED_INTERFACES
    )


def zero_fill(matchobj):
    return matchobj.group().zfill(4)


num_sort_regex = re.compile(r"\d+")


@indexer(Interface)
def sortable_title(obj):
    """Helper method for to provide FieldIndex for Title."""
    title = getattr(obj, "Title", None)
    if title is not None:
        if safe_callable(title):
            title = title()

        if isinstance(title, str):
            # Ignore case, normalize accents, strip spaces
            sortabletitle = mapUnicode(safe_text(title)).lower().strip()
            # Replace numbers with zero filled numbers
            sortabletitle = num_sort_regex.sub(zero_fill, sortabletitle)
            return sortabletitle
    return ""


@indexer(Interface)
def getObjPositionInParent(obj):
    """Helper method for catalog based folder contents."""
    parent = aq_parent(aq_inner(obj))
    ordered = IOrderedContainer(parent, None)
    if ordered is not None:
        return ordered.getObjectPosition(obj.getId())
    return 0


@indexer(Interface)
def getObjSize(obj):
    """Helper method for catalog based folder contents."""
    if base_hasattr(obj, "get_size"):
        size = obj.get_size()
    else:
        size = 0

    return human_readable_size(size)


@indexer(Interface)
def is_folderish(obj):
    """Should this item be treated as a folder?

    Checks isPrincipiaFolderish, as well as the INonStructuralFolder
    interfaces.
    """
    # If the object explicitly states it doesn't want to be treated as a
    # structural folder, don't argue with it.
    folderish = bool(getattr(aq_base(obj), "isPrincipiaFolderish", False))
    return folderish and not INonStructuralFolder.providedBy(obj)


@indexer(Interface)
def is_default_page(obj):
    """Is this the default page in its folder"""
    ptool = getToolByName(obj, "plone_utils", None)
    if ptool is None:
        return False
    return ptool.isDefaultPage(obj)


@indexer(Interface)
def getIcon(obj):
    """
    geticon redefined in Plone > 5.0
    see https://github.com/plone/Products.CMFPlone/issues/1226

    reuse of metadata field,
    now used for showing thumbs in content listings etc.
    when obj is an image or has a lead image
    or has an image field with name 'image': true else false
    """
    img_field = getattr(obj.aq_base, "image", False)
    return bool(IImage.providedBy(img_field))


@indexer(Interface)
def mime_type(obj):
    return aq_base(obj).getPrimaryField().getContentType(obj)


@implementer(IPloneCatalogTool)
class CatalogTool(PloneBaseTool, BaseTool):
    """Plone's catalog tool"""

    meta_type = "Plone Catalog Tool"
    security = ClassSecurityInfo()
    toolicon = "skins/plone_images/book_icon.png"
    _counter = None

    manage_catalogAdvanced = DTMLFile("www/catalogAdvanced", globals())

    manage_options = (
        {"action": "manage_main", "label": "Contents"},
        {"action": "manage_catalogView", "label": "Catalog"},
        {"action": "manage_catalogIndexes", "label": "Indexes"},
        {"action": "manage_catalogSchema", "label": "Metadata"},
        {"action": "manage_catalogAdvanced", "label": "Advanced"},
        {"action": "manage_catalogReport", "label": "Query Report"},
        {"action": "manage_catalogPlan", "label": "Query Plan"},
        {"action": "manage_propertiesForm", "label": "Properties"},
    )

    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    def _removeIndex(self, index):
        # Safe removal of an index.
        try:
            self.manage_delIndex(index)
        except Exception:
            pass

    def _listAllowedRolesAndUsers(self, user):
        # Makes sure the list includes the user's groups.
        result = user.getRoles()
        if "Anonymous" in result:
            # The anonymous user has no further roles
            return ["Anonymous"]
        result = list(result)
        if hasattr(aq_base(user), "getGroups"):
            groups = ["user:%s" % x for x in user.getGroups()]
            if groups:
                result = result + groups
        # Order the arguments from small to large sets
        result.insert(0, "user:%s" % user.getId())
        result.append("Anonymous")
        return result

    @security.private
    def indexObject(self, object, idxs=None):
        # Add object to catalog.
        # The optional idxs argument is a list of specific indexes
        # to populate (all of them by default).
        if idxs is None:
            idxs = []
        self.reindexObject(object, idxs)

    @security.protected(ManageZCatalogEntries)
    def catalog_object(
        self, object, uid=None, idxs=None, update_metadata=1, pghandler=None
    ):
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

        ZCatalog.catalog_object(
            self, w, uid, idxs, update_metadata, pghandler=pghandler
        )

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
        processQueue()
        return self._counter is not None and self._counter() or 0

    @security.private
    def allow_inactive(self, query_kw):
        """Check, if the user is allowed to see inactive content.
        First, check if the user is allowed to see inactive content site-wide.
        Second, if there is a 'path' key in the query, check if the user is
        allowed to see inactive content for these paths.
        Conservative check: as soon as one path is disallowed, return False.
        If a path cannot be traversed, ignore it.
        """
        allow_inactive = _checkPermission(AccessInactivePortalContent, self)
        if allow_inactive:
            return True

        paths = query_kw.get("path", False)
        if not paths:
            return False

        if isinstance(paths, dict):
            # Like: {'path': {'depth': 0, 'query': ['/Plone/events/']}}
            # Or: {'path': {'depth': 0, 'query': '/Plone/events/'}}
            paths = paths.get("query", [])

        if isinstance(paths, str):
            paths = [paths]

        objs = []
        site = getSite()
        for path in list(paths):
            try:
                site_path = "/".join(site.getPhysicalPath())
                parts = path[len(site_path) + 1 :].split("/")
                parent = site.unrestrictedTraverse("/".join(parts[:-1]))
                objs.append(parent.restrictedTraverse(parts[-1]))
            except (KeyError, AttributeError, Unauthorized):
                # When no object is found don't raise an error
                pass

        if not objs:
            return False

        allow = True
        for ob in objs:
            allow = allow and _checkPermission(AccessInactivePortalContent, ob)

        return allow

    @security.protected(SearchZCatalog)
    def searchResults(self, query=None, **kw):
        # Calls ZCatalog.searchResults with extra arguments that
        # limit the results to what the user is allowed to see.
        #
        # This version uses the 'effectiveRange' DateRangeIndex.
        #
        # It also accepts a keyword argument show_inactive to disable
        # effectiveRange checking entirely even for those without portal
        # wide AccessInactivePortalContent permission.

        # Make sure any pending index tasks have been processed
        processQueue()

        kw = kw.copy()
        show_inactive = kw.get("show_inactive", False)
        if isinstance(query, dict) and not show_inactive:
            show_inactive = "show_inactive" in query

        user = _getAuthenticatedUser(self)
        kw["allowedRolesAndUsers"] = self._listAllowedRolesAndUsers(user)

        if not show_inactive and not self.allow_inactive(kw):
            kw["effectiveRange"] = DateTime()

        # filter out invalid sort_on indexes
        sort_on = kw.get("sort_on") or []
        if isinstance(sort_on, str):
            sort_on = [sort_on]
        valid_indexes = self.indexes()
        try:
            sort_on = [idx for idx in sort_on if idx in valid_indexes]
        except TypeError:
            # sort_on is not iterable
            sort_on = []
        if not sort_on:
            kw.pop("sort_on", None)
        else:
            kw["sort_on"] = sort_on

        return ZCatalog.searchResults(self, query, **kw)

    __call__ = searchResults

    def search(self, query, sort_index=None, reverse=0, limit=None, merge=1):
        # Wrap search() the same way that searchResults() is

        # Make sure any pending index tasks have been processed
        processQueue()

        user = _getAuthenticatedUser(self)
        query["allowedRolesAndUsers"] = self._listAllowedRolesAndUsers(user)

        if not self.allow_inactive(query):
            query["effectiveRange"] = DateTime()

        return super().search(query, sort_index, reverse, limit, merge)

    @security.protected(ManageZCatalogEntries)
    def clearFindAndRebuild(self):
        # Empties catalog, then finds all contentish objects (i.e. objects
        # with an indexObject method), and reindexes them.
        # This may take a long time.
        idxs = list(self.indexes())

        def indexObject(obj, path):
            if (
                obj != self
                and base_hasattr(obj, "reindexObject")
                and safe_callable(obj.reindexObject)
            ):
                try:
                    self.reindexObject(obj, idxs=idxs)
                    # index conversions from plone.app.discussion
                    annotions = IAnnotations(obj)
                    if DISCUSSION_ANNOTATION_KEY in annotions:
                        conversation = annotions[DISCUSSION_ANNOTATION_KEY]
                        conversation = conversation.__of__(obj)
                        for comment in conversation.getComments():
                            try:
                                self.indexObject(comment, idxs=idxs)
                            except StopIteration:  # pragma: no cover
                                pass
                except TypeError:
                    # Catalogs have 'indexObject' as well, but they
                    # take different args, and will fail
                    pass

        self.manage_catalogClear()
        portal = aq_parent(aq_inner(self))
        indexObject(portal, "")
        portal.ZopeFindAndApply(portal, search_sub=True, apply_func=indexObject)

    @security.protected(ManageZCatalogEntries)
    def manage_catalogRebuild(self, RESPONSE=None, URL1=None):
        """Clears the catalog and indexes all objects with an 'indexObject'
        method. This may take a long time.
        """
        elapse = time.time()
        c_elapse = process_time()

        self.clearFindAndRebuild()

        elapse = time.time() - elapse
        c_elapse = process_time() - c_elapse

        msg = (
            "Catalog Rebuilt\n"
            "Total time: %s\n"
            "Total CPU time: %s" % (repr(elapse), repr(c_elapse))
        )
        logger.info(msg)

        if RESPONSE is not None:
            RESPONSE.redirect(
                URL1
                + "/manage_catalogAdvanced?manage_tabs_message="
                + urllib.parse.quote(msg)
            )


InitializeClass(CatalogTool)
