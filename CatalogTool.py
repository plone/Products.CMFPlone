from Products.CMFCore.CatalogTool import CatalogTool as BaseTool
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class CatalogTool(BaseTool):

    meta_type = ToolNames.CatalogTool
    security = ClassSecurityInfo()

    def manage_afterAdd(self, item, container):

        if item is self:
            class args:
                def __init__(self, **kw):
                    self.__dict__.update(kw)
            
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


CatalogTool.__doc__ = BaseTool.__doc__

InitializeClass(CatalogTool)
