from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFCore.utils import _getAuthenticatedUser, _checkPermission
from Products.CMFCore.CMFCorePermissions import AccessInactivePortalContent
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from DateTime import DateTime

try: 
    import Products.TextIndexNG2
    txng_version = 2
except ImportError:
    txng_version = 0

class CatalogTool(BaseTool):

    meta_type = ToolNames.CatalogTool
    security = ClassSecurityInfo()

    def manage_afterAdd(self, item, container):
        # Makes sure the SearchableText index is a ZCTextIndex

        class args:
            def __init__(self, **kw):
                self.__dict__.update(kw)
            def keys(self):
                return self.__dict__.keys()

        if txng_version == 2:
            """ Prefer TextIndexNG V2 if available instead of ZCTextIndex """

            extra = args(default_encoding='utf-8')
            self.manage_delIndex(['SearchableText', 'Title', 'Description'])
            self.manage_addIndex('SearchableText', 'TextIndexNG2', 
                                  extra=args(default_encoding='utf-8', 
                                             use_converters=1, autoexpand=1))
            self.manage_addIndex('Title', 'TextIndexNG2', extra=extra)
            self.manage_addIndex('Description', 'TextIndexNG2', extra=extra)
            self.manage_delObjects('Vocabulary')

        else:

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

                self.manage_delIndex(['SearchableText'])
                self.manage_addIndex('SearchableText', 'ZCTextIndex', extra=extra)

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
        '''Add to catalog.
        '''
        url = self.__url(object)
        self.catalog_object(object, url, idxs)

CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
