## Script (Python) "navigation_tree_builder"
##parameters=tree_root
##title=Standard Tree
##

from Products.CMFPlone.StatelessTreeNav import StatelessTreeBuilder
from Products.CMFPlone.StatelessTreeNav import wrap_obj
from Products.CMFCore.utils import getToolByName

def childFinder(obj,folderishOnly=1):
    if obj.meta_type == 'Portal Topic':
        cat = getToolByName( obj, 'portal_catalog' )

        res=obj.listFolderContents()
        subs=obj.queryCatalog()
        for s in subs:
            o=context.restrictedTraverse(cat.getpath(s.data_record_id_))
            res.append(wrap_obj(o,obj))
        
    else:    
        if hasattr(obj,'listFolderContents'):
            res=obj.listFolderContents()
        else:
            res=obj.objectValues()

    if folderishOnly:
        return filter(lambda x: hasattr(x,'isPrincipiaFolderish') and x.isPrincipiaFolderish,res)
    else:
        return res
    

tb=StatelessTreeBuilder(context,childFinder=childFinder,includeTop=0,
showFolderishSiblingsOnly=1,showFolderishChildrenOnly=1)

return tb.buildFlatMenuStructure()

