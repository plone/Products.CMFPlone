from types import StringType, UnicodeType
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime
from AccessControl import Unauthorized, getSecurityManager

from StatelessTreeNav import StatelessTreeBuilder
from Products.CMFCore.utils import getToolByName

def constructNavigationTreeViewBuilder(self, **kwargs):
    """ """
    ntvb=NavigationTreeViewBuilder(**kwargs)
    return ntvb

class NavigationTreeViewBuilder(SimpleItem):
    """ Please do not attach this object to the ZODB graph """

    def __init__(self, **kwargs):
        setattr(self, 'ids', kwargs.keys())
        for k, v in kwargs.items():
            setattr(self, k, v)

    def getContext(self):
        return self.aq_parent.aq_parent

    def __call__(self):
        """ return the data structure """
        context=self.getContext()

        navtree_properties=getToolByName(self, 'portal_properties').navtree_properties
        props=getattr(context,'navtree_properties', navtree_properties)
        #XXX The above is highly inefficient I believe

        for k, v in props.propertyItems():
            if getattr(self, k, None) is None:
                setattr(self, k, getattr(context, k, v))

        self.sortCriteria=[c for c in self.sortCriteria
                           if type(c) in (UnicodeType, StringType) and c.strip()]

        tb=StatelessTreeBuilder(context, topObject=self.tree_root,
          childFinder=self.childFinder, includeTop=self.includeTop,
          showFolderishSiblingsOnly=self.showFolderishSiblingsOnly,
          showFolderishChildrenOnly=self.showFolderishChildrenOnly,
          showNonFolderishObject=self.showNonFolderishObject,
          topLevel=self.topLevel, forceParentsInBatch=self.forceParentsInBatch,
          skipIndex_html=self.skipIndex_html,bottomLevel=self.bottomLevel,
          idsNotToList=getattr(self,'idsNotToList',[])
          )

        batchStart=None
        batchSize=self.batchSize
        if self.navBatchStart is None:
            batchStart=None
        else:
            batchStart=int(self.navBatchStart)

        #from where to start? is called automatically by the .pt
        res=tb.buildFlatMenuStructure( batchSize=batchSize,
                                       batchStart=batchStart )

        for r in res['list']:
            r['published'] = self.checkPublished(r['object'])

        return res

    # checks if an object is published respecting its
    # publishing dates
    # XXX I did not find this in the API but there
    # should be something like this....
    def checkPublished(self, o):
        user=getSecurityManager().getUser()
        showUnpublishedContent = user.has_role(self.rolesSeeUnpublishedContent,o)
        try:
            if showUnpublishedContent:
                return showUnpublishedContent

            workflow_tool = getToolByName(self, 'portal_workflow')
            if workflow_tool.getInfoFor(o,'review_state','') != 'published':
                return 0
            now     = DateTime()
            start_pub = getattr(o,'effective_date',None)
            end_pub   = getattr(o,'expiration_date',None)
            if start_pub and start_pub > now:
                return 0
            if end_pub and now > end_pub:
                return 0
        except:
            return 0
        return 1

    #default function that finds the children out of a folderish object
    def childFinder(self,obj,folderishOnly=1):
        user=getSecurityManager().getUser()
        portal=self.aq_parent.aq_inner
        catalog=portal.portal_catalog
        getpath=catalog.getpath
        perm_check=portal.portal_membership.checkPermission

        # the 'important' users may see unpublished content
        # who can see unpublished content may also see hidden files
        showHiddenFiles = user.has_role(self.rolesSeeHiddenContent or [],obj)

        try:
            if obj.meta_type in self.parentMetaTypesNotToQuery:
                return []

            # shall all Members be listed or just myself!
            if self.showMyUserFolderOnly and obj == portal.portal_membership.getMembersFolder():
                try:
                    return [getattr(obj,user.getId())]
                except:
                    return []

            # to traverse through Portal Topics
            if obj.meta_type == 'Portal Topic':
                #in order to view all topic results in the tree
                folderishOnly=not self.showTopicResults
                res=obj.listFolderContents(suppressHiddenFiles=not showHiddenFiles)
                subs=obj.queryCatalog()

                # get the objects out of the cat results
                for s in subs:
                    try:
                        o=context.restrictedTraverse(getpath(s.data_record_id_))
                        res.append(wrap_obj(o,obj))
                    except (Unauthorized, 'Unauthorized'):
                        pass
            else:
                #traversal to all 'CMFish' folders
                if hasattr(obj.aq_explicit,'listFolderContents'):
                    try:
                        res=obj.listFolderContents(suppressHiddenFiles=not showHiddenFiles)
                    except TypeError:
                        # if the suppressHiddenFiles param is not supported
                        res=obj.listFolderContents()
                else:
                    res=obj.contentValues()    #and all other *CMF* folders

            rs=[]
            for r in res: #filter out metatypes and by except:pass
                          #all objs producing an error
                try:
                    if r.meta_type not in self.metaTypesNotToList and r.id not in self.idsNotToList:
                        rs.append(r)
                except :
                    pass
            res=rs

            # if wanted just keep folderish objects
            if folderishOnly:
                objs=[x for x in res if getattr(x,'isPrincipiaFolderish',None)]
                perm = 'View' #XXX should be imported
                res = [o for o in objs if perm_check(perm, o)]

            res = [o for o in res if self.checkPublished(o) ]

            try:
                res.sort(self._navtree_cmp) #if sorting fails - never mind, it shall not break nav
            except:
                pass
            return res
        except :
            return []


    def _navtree_cmp(self, a,b):
        for cs in self.sortCriteria:
            c=cs.split(',')
            field=c[0]
            if len(c)==2:
                order=c[1]
            else:
                order='asc'
            if hasattr(a,field) and hasattr(b,field):
                aval=getattr(a,field)
                if callable(aval): aval = aval()
                bval=getattr(b,field)
                if callable(bval): bval = bval()

                if order == 'desc':
                    aval,bval = bval,aval
                try:
                    aval=aval.lower()
                    bval=bval.lower()
                except AttributeError:
                    pass

                if aval < bval:
                    return -1
                elif bval < aval:
                    return 1
        return 0
