## Script (Python) "navigation_tree_builder"
##parameters=tree_root,navBatchStart=0
##title=Standard Tree
##
#Stateless Tree Navigation
#(c) Philipp Auersperg phil@bluedynamics.com 10.09.2002


from Products.CMFPlone.StatelessTreeNav import StatelessTreeBuilder
from Products.CMFPlone.StatelessTreeNav import wrap_obj
from Products.CMFCore.utils import getToolByName

#default function that finds the children out of a folderish object
def childFinder(obj,folderishOnly=1):
    if obj.meta_type == 'Portal Topic':
        # to traverse through Portal Topics
        cat = getToolByName( obj, 'portal_catalog' )
        
        #folderishOnly=0 #in order to view all topic results in the tree 

        res=obj.listFolderContents()
        subs=obj.queryCatalog()
        
        # get the objects out of the cat results
        for s in subs:
            o=context.restrictedTraverse(cat.getpath(s.data_record_id_))
            res.append(wrap_obj(o,obj))
        
    else:    
        #traversal to all 'CMFish' folders
        if hasattr(obj.aq_explicit,'listFolderContents'):
            res=obj.listFolderContents()
            #raise 'res:',res
        else:
            #... and all other folders
            res=obj.objectValues()

    # if wanted just keep folderish objects
    if folderishOnly:
        return filter(lambda x: hasattr(x.aq_explicit,'isPrincipiaFolderish') and x.aq_explicit.isPrincipiaFolderish,res)
    else:
        return res

tb=StatelessTreeBuilder(context,childFinder=childFinder,
        includeTop=1, #if set, the top object itself is included in the tree
        showFolderishSiblingsOnly=1, #in the hierarchy above the leaf object
                                     #just folders should be displayed
        showFolderishChildrenOnly=1, #list only folders below the leaf object
        showNonFolderishObject=0)    #if the leaf object is not a folder 
                                     #and showFolderishChildrenOnly the leaf is
                                     # displayed in any case, but not its siblings

return tb.buildFlatMenuStructure(
    batchSize=30, # how long should one batch be
                  # per definition it stops not before the leaf object is reached
    batchStart=int(navBatchStart) #from where to start? is called automatically by the .pt
    )

