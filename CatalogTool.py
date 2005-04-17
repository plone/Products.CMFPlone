#
# Plone CatalogTool
#

from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.CMFCore.CatalogTool import IndexableObjectWrapper, _mergedLocalRoles
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

from Products.ZCatalog.ZCatalog import ZCatalog
from AccessControl.Permissions import manage_zcatalog_entries as ManageZCatalogEntries
from AccessControl.PermissionRole import rolesForPermissionOn

from Acquisition import aq_base


# Use TextIndexNG2 if installed
try: 
    import Products.TextIndexNG2
    txng_version = 2
except ImportError:
    txng_version = 0


class IndexableObjectWrapper(IndexableObjectWrapper):
    """
    We override CMF's IndexableObjectWrapper class to use GRUF's custom
    allowedRolesAndUsers method if available.
    """
    def allowedRolesAndUsers(self):
        """
        Return a list of roles and users with View permission.
        Used by PortalCatalog to filter out items you're not allowed to see.
        """
        ob = self.__ob
        allowed = {}
        for r in rolesForPermissionOn('View', ob):
            allowed[r] = 1
        try:
            localroles = self.acl_users._getAllLocalRoles(self)
        except AttributeError:
            localroles = _mergedLocalRoles(ob)
        for user, roles in localroles.items():
            for role in roles:
                if allowed.has_key(role):
                    allowed['user:' + user] = 1
        if allowed.has_key('Owner'):
            del allowed['Owner']
        return list(allowed.keys())


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

        return ( ('Subject', 'KeywordIndex')
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
        '''Add object to catalog.
        The optional idxs argument is a list of specific indexes
        to populate (all of them by default).
        '''
        self.reindexObject(object, idxs)

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=[], update_metadata=1):
        '''Update catalog after object data has changed.
        The optional idxs argument is a list of specific indexes
        to update (all of them by default).
        The update_metadata flag controls whether the object's
        metadata record is updated as well.
        '''
        url = self.__url(object)
        if idxs != []:
            # Filter out invalid indexes.
            valid_indexes = self._catalog.indexes.keys()
            idxs = [i for i in idxs if i in valid_indexes]
        self.catalog_object(object, url, idxs, update_metadata)

    security.declareProtected(ManageZCatalogEntries, 'catalog_object')
    def catalog_object(self, object, uid, idxs=[], update_metadata=1):
        # Wraps the object with workflow and accessibility
        # information just before cataloging.
        wf = getattr(self, 'portal_workflow', None)
        if wf is not None:
            vars = wf.getCatalogVariablesFor(object)
        else:
            vars = {}
        w = IndexableObjectWrapper(vars, object)
        try:
            ZCatalog.catalog_object(self, w, uid, idxs, update_metadata)
        except TypeError:
            ZCatalog.catalog_object(self, w, uid, idxs)


CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
