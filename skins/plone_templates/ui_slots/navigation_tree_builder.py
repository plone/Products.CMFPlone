## Script (Python) "navigation_tree_builder"
##parameters=tree_root,navBatchStart=0,showMyUserFolderOnly=1
##title=Standard Tree
##
#Stateless Tree Navigation
#(c) Philipp Auersperg phil@bluedynamics.com 10.09.2002


from Products.CMFPlone.StatelessTreeNav import StatelessTreeBuilder
from Products.CMFPlone.StatelessTreeNav import wrap_obj
from Products.CMFCore.utils import getToolByName

# put in here the meta_types not to be listed
metaTypesNotToList=['CMF Collector','CMF Collector Issue','CMF Collector Catalog']
# there is some VERY weird error with Collectors,
# so I have to remove from the list

# these types should not be queried for children
parentMetaTypesNotToQuery=[]

#default function that finds the children out of a folderish object
def childFinder(obj,folderishOnly=1):
    if obj.meta_type in parentMetaTypesNotToQuery:
        return []
    
    # shall all Members be listed or just myself!
    if showMyUserFolderOnly and obj.id=='Members':
        try:
            return [getattr(obj,obj.REQUEST['AUTHENTICATED_USER'].getId())]
        except:
            return []
    
##    if folderishOnly:
##        return obj.objectValues(['Plone Folder'])
##    else:
##        return obj.objectValues()
    
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
        else:
            #and all other *CMF* folders
            res=obj.contentValues()
    
    res = filter (lambda x:x.meta_type not in metaTypesNotToList,res)

    # if wanted just keep folderish objects
    if folderishOnly:
        objs=filter(lambda x: hasattr(x.aq_explicit,'isPrincipiaFolderish') and x.aq_explicit.isPrincipiaFolderish,res)
        perm = 'List folder contents' #XXX should be imported
        permChk = context.portal_membership.checkPermission
        return [o for o in objs if permChk(perm, o)] #XXX holy jeebus! this is expensive need to cache!
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

