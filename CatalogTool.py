#
# Plone CatalogTool
#
import re

from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.CMFCorePermissions import AccessInactivePortalContent
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_base
from DateTime import DateTime

from Products.CMFCore.utils import _getAuthenticatedUser
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.CatalogTool import _mergedLocalRoles
from Products.CMFCore.interfaces.portal_catalog \
        import IndexableObjectWrapper as IIndexableObjectWrapper
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_callable
from OFS.IOrderSupport import IOrderedContainer
from ZODB.POSException import ConflictError

from Products.ZCatalog.ZCatalog import ZCatalog

from AccessControl.Permissions import manage_zcatalog_entries as ManageZCatalogEntries
from AccessControl.Permissions import search_zcatalog as SearchZCatalog
from AccessControl.PermissionRole import rolesForPermissionOn

# Use TextIndexNG2 if installed
try: 
    import Products.TextIndexNG2
    txng_version = 2
except ImportError:
    txng_version = 0

_marker = object()


class ExtensibleIndexableObjectRegistry(dict):
    """Registry for extensible object indexing
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
    """Extensible wrapper for object indexing
    
    vars - additional vars as a dict, used for workflow vars like review_state
    obj - the indexable object
    portal - the portal root object
    registry - a registry 
    **kwargs - additional keyword arguments
    """
    
    __implements__ = IIndexableObjectWrapper
    
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
    """
    Return a list of roles and users with View permission.
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
    """Helper method for to provide FieldIndex for Title
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
    """Helper method for catalog based folder contents
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
    """Helper method for catalog based folder contents
    """
    smaller = SIZE_ORDER[-1]

    if base_hasattr(obj, 'get_size'):
        size=obj.get_size()
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
    """Should this item be treated as a folder? Checks isPrincipiaFolderish,
    as well as the INonStructuralFolder interface.
    """
    # If the object explicitly states it doesn't want to be treated as a
    # structural folder, don't argue with it.
    if INonStructuralFolder.isImplementedBy(obj):
        return False
    else:
        return bool(getattr(aq_base(obj), 'isPrincipiaFolderish', False))

registerIndexableAttribute('is_folderish', is_folderish)


def syndication_enabled(obj, **kwargs):
    """Get state of syndication
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
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__)

    def __init__(self):
        ZCatalog.__init__(self, self.getId())
        self._initIndexes()
        
    security.declarePublic('enumerateIndexes') 
    def enumerateIndexes(self):

        idxs = ( ('Subject', 'KeywordIndex')
               , ('Creator', 'FieldIndex')
               , ('Date', 'DateIndex')
               , ('Type', 'FieldIndex')
               , ('created', 'DateIndex')
               , ('effective', 'DateIndex')
               , ('expires', 'DateIndex')
               , ('modified', 'DateIndex')
               , ('allowedRolesAndUsers', 'KeywordIndex')
               , ('review_state', 'FieldIndex')
               , ('in_reply_to', 'FieldIndex')
               , ('meta_type', 'FieldIndex')
               , ('id', 'FieldIndex')
               , ('getId', 'FieldIndex')
               , ('path', 'ExtendedPathIndex')
               , ('portal_type', 'FieldIndex')
               , ('getObjPositionInParent', 'FieldIndex')
               , ('is_folderish', 'FieldIndex')
               , ('is_default_page', 'FieldIndex')
               )
        return tuple([(n, t, None) for n, t in idxs])

    security.declarePublic( 'enumerateColumns' )
    def enumerateColumns( self ):
        #   Return a sequence of schema names to be cached.
        #   Creator is deprecated and may go away, use listCreators!
        return ( 'Subject'
               , 'Title'
               , 'Description'
               , 'Type'
               , 'review_state'
               , 'Creator'
               , 'listCreators'
               , 'Date'
               , 'getIcon'
               , 'created'
               , 'effective'
               , 'expires'
               , 'modified'
               , 'CreationDate'
               , 'EffectiveDate'
               , 'ExpirationDate'
               , 'ModificationDate'
               , 'getId'
               , 'portal_type'
               # plone metadata
               , 'id', # BBB to be removed in Plone 2.2
               'getObjSize',
               'exclude_from_nav',
               )

    def _removeIndex(self, index):
        """ Safe removal of an index """
        try: self.manage_delIndex(index)
        except: pass

    def manage_afterAdd(self, item, container):
        self._createTextIndexes(item, container)
               
    def _createTextIndexes(self, item, container):
        """ In addition to the standard indexes we need to create 
            'SearchableText', 'Title' and 'Description' either as
            TextIndexNG2 or ZCTextIndex instance
        """

        class args:
            def __init__(self, **kw):
                self.__dict__.update(kw)
            def keys(self):
                return self.__dict__.keys()

        # We need to remove the indexes to keep the tests working...baaah
        for idx in ('SearchableText', 'Title', 'Description'):
            self._removeIndex(idx)

        if txng_version == 2:

            # Prefer TextIndexNG V2 if available instead of ZCTextIndex 

            extra = args(default_encoding='utf-8')
            self.manage_addIndex('SearchableText', 'TextIndexNG2', 
                                  extra=args(default_encoding='utf-8', 
                                             use_converters=1, autoexpand=1))
            self.manage_addIndex('Title', 'TextIndexNG2', extra=extra)
            self.manage_addIndex('Description', 'TextIndexNG2', extra=extra)

        else:

            # ZCTextIndex as fallback

            if item is self and not hasattr(aq_base(self), 'plone_lexicon'):

                self.manage_addProduct[ 'ZCTextIndex' ].manage_addLexicon(
                    'plone_lexicon',
                    elements=[
                    args(group= 'Case Normalizer' , name= 'Case Normalizer' ),
                    args(group= 'Stop Words' , name= " Don't remove stop words" ),
                    args(group= 'Word Splitter' , name= "Unicode Whitespace splitter" ),
                    ]
                    )

                extra = args( doc_attr = 'SearchableText',
                              lexicon_id = 'plone_lexicon',
                              index_type  = 'Okapi BM25 Rank' )
                self.manage_addIndex('SearchableText', 'ZCTextIndex', extra=extra)

                extra = args( doc_attr = 'Description',
                              lexicon_id = 'plone_lexicon',
                              index_type  = 'Okapi BM25 Rank' )
                self.manage_addIndex('Description', 'ZCTextIndex', extra=extra)

                extra = args( doc_attr = 'Title',
                              lexicon_id = 'plone_lexicon',
                              index_type  = 'Okapi BM25 Rank' )
                self.manage_addIndex('Title', 'ZCTextIndex', extra=extra)

    security.declareProtected(ManagePortal, 'migrateIndexes')
    def migrateIndexes(self):
        """ Recreate all indexes """
        self._initIndexes()
        self._createTextIndexes()

    def _listAllowedRolesAndUsers( self, user ):
        # Makes sure the list includes the user's groups
        result = list( user.getRoles() )
        if hasattr(aq_base(user), 'getGroups'):
            result = result + ['user:%s' % x for x in user.getGroups()]
        result.append( 'Anonymous' )
        result.append( 'user:%s' % user.getId() )
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
        try:
            # pghandler argument got added in Zope 2.8
            ZCatalog.catalog_object(self, w, uid, idxs,
                                    update_metadata, pghandler=pghandler)
        except TypeError:
            try:
                # update_metadata argument got added somewhere into
                # the Zope 2.6 line (?)
                ZCatalog.catalog_object(self, w, uid, idxs, update_metadata)
            except TypeError:
                ZCatalog.catalog_object(self, w, uid, idxs)

    security.declareProtected(SearchZCatalog, 'searchResults')
    def searchResults(self, REQUEST=None, **kw):
        """ Calls ZCatalog.searchResults with extra arguments that
            limit the results to what the user is allowed to see.

            This version uses the 'effectiveRange' DateRangeIndex.

            It also accepts a keyword argument show_inactive to disable
            effectiveRange checking entirely even for those withot portal wide
            AccessInactivePortalContent permission.
        """
        kw = kw.copy()
        show_inactive = kw.get('show_inactive', False)

        user = _getAuthenticatedUser(self)
        kw['allowedRolesAndUsers'] = self._listAllowedRolesAndUsers(user)

        if not show_inactive and not _checkPermission(AccessInactivePortalContent, self):
            kw['effectiveRange'] = DateTime()
            if kw.has_key('effective'):
                del kw['effective']
            if kw.has_key('expires'):
                del kw['expires']

        return ZCatalog.searchResults(self, REQUEST, **kw)

    __call__ = searchResults

CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
