# Stateless Tree Navigation for Plone
# (c) Philipp Auersperg phil@bluedynamics.com 10.09.2002

import string
from Globals import HTML
from AccessControl import ClassSecurityInfo,ModuleSecurityInfo,allow_class,allow_module

# to be able to import this stuff into python scripts
ModuleSecurityInfo('Products.CMFPlone').declarePublic('StatelessTreeNav')
ModuleSecurityInfo('Products.CMFPlone.StatelessTreeNav').declarePublic('StatelessTreeBuilder')
allow_module('Products.CMFPlone.StatelessTreeNav')

def wrap_obj(o,parent):
    return o.__of__(parent)

def setupNavTreePropertySheet(prop_tool):
    ''' sets up the default propertysheet for the navtree '''

    prop_tool.manage_addPropertySheet('navtree_properties', 'NavigationTree properties')
    p=prop_tool.navtree_properties
    p._setProperty('showMyUserFolderOnly', 1, 'boolean')
    p._setProperty('includeTop', 1, 'boolean')
    p._setProperty('showFolderishSiblingsOnly', 1, 'boolean')
    p._setProperty('showFolderishChildrenOnly', 1, 'boolean')
    p._setProperty('showNonFolderishObject', 0, 'boolean')
    p._setProperty('topLevel', 0, 'int')
    p._setProperty('batchSize', 30, 'int')
    p._setProperty('showTopicResults', 1, 'boolean')
    p._setProperty('rolesSeeUnpublishedContent', ['Manager','Reviewer','Owner'] , 'lines')
    p._setProperty('sortCriteria', ['isPrincipiaFolderish,desc','title_or_id,asc']  , 'lines')
    p._setProperty('metaTypesNotToList',['CMF Collector','CMF Collector Issue','CMF Collector Catalog'],'lines')
    p._setProperty('parentMetaTypesNotToQuery',[],'lines')
    p._setProperty('croppingLength',18,'int')
    p._setProperty('forceParentsInBatch',0,'boolean')
    p._setProperty('skipIndex_html',1,'boolean')
    p._setProperty('rolesSeeContentsView', ['Manager','Reviewer','Owner'] , 'lines')
    p._setProperty('rolesSeeHiddenContent', ['Manager',] , 'lines')

class StatelessTreeBuilder:
    """ builds a stateless tree structure for objects """

    security=ClassSecurityInfo()

    def __init__(self, object, topObject=None, topMetaType='CMF Site',
            maxcount=65535,includeTop=0,topLevel=0,listSiblings=1,
            childFinder=None,showFolderishSiblingsOnly=0,showFolderishChildrenOnly=0,
            showNonFolderishObject=0,forceParentsInBatch=0,skipIndex_html=0):

        self.object=object
        self.topObject=topObject
        self.topMetaType=topMetaType
        self.includeTop=includeTop
        self.maxcount=maxcount
        self.listSiblings=listSiblings
        self.childFinder=childFinder
        self.showFolderishSiblingsOnly=showFolderishSiblingsOnly
        self.showFolderishChildrenOnly=showFolderishChildrenOnly
        self.showNonFolderishObject=showNonFolderishObject
        self.forceParentsInBatch=forceParentsInBatch
        self.skipIndex_html=skipIndex_html
        
        if topLevel >= 0:
            self.topLevel=topLevel
        else:
            #negative topLevel is calculated relative to the object itself
            l=self.getLevel(object)
            if object.isPrincipiaFolderish:
                self.topLevel=max(0,l+topLevel+1)
            else:
                self.topLevel=max(0,l+topLevel+0)
                
    security.declarePublic('getLevel')
    def getLevel (self,object=None):
        """
        returns the depth of an object position relative to a given meta_type or object
        """

        count=0
        par = object
        if par is None:
            par = self.object

        while ( hasattr(par,'meta_type') and str(par.meta_type) != str(self.topMetaType)
            and self.topObject != par and count < int(self.maxcount) ) :

            par=par.aq_parent
            count=count+1

        return count

    security.declarePublic('getParentObjects')
    def getParentObjects (self,reversed=1):
        """
        This function returns the objects in the parent path beginning with the self itself
        They are used in menus.
        """

        import string

        res=[]
        count=0
        level=self.getLevel()
        par = self.object

        if not par.isPrincipiaFolderish:
            par=par.aq_parent

        while (hasattr(par,'meta_type') and str(par.meta_type) != str(self.topMetaType)
            and self.topObject != par ): #and count < int(self.maxcount) and level > self.topLevel) :
            res.append(par)
            par=par.aq_parent
            count=count+1
            level=level-1

        if self.includeTop :
            res.append(par)

        if reversed:
            res.reverse()

        return res

    def getChildObjects(self,object,folderishOnly=0):
        ''' called by buildMenuStructure
            is overridable if self.childFinder is set -> array of objects
        '''

        if hasattr(object,'isPrincipiaFolderish') and object.isPrincipiaFolderish:
            if self.childFinder:
                return self.childFinder(object,folderishOnly)

            if folderishOnly:return object.objectValues(['Folder','PloneFolder'])
            else:return object.objectValues()
        else:
            return []

    security.declarePublic('buildMenuStructure')
    def buildMenuStructure (self):
        """ builds a menu structure :) """
        res=[]
        itemcount=0
        path=self.getParentObjects()

        count=0
        p=None

        for p in path:

            r={'object':p,'level':None,'siblings':[],'title':p.title_or_id(),'url':p.absolute_url()}

            try:
                r['level']=self.getLevel(p)
            except:
                pass

            if self.listSiblings == 1:
                if self.includeTop and p==path[0]:
                    r['siblings']=[p]
                else:
                    r['siblings']=self.getChildObjects(p.aq_parent,self.showFolderishSiblingsOnly)
                    r['siblingtitles']=map(lambda x:x.title_or_id(),r['siblings'])
                    if p not in r['siblings']:
                        r['siblings'].append(p)

            res.append(r)
            itemcount=itemcount+1

            if len(r['siblings']):
                itemcount=itemcount+len(r['siblings'])-1

            count=count+1

        if p:
            o=self.object
            level=r['level']+1
        else:
            o=self.object
            level=self.getLevel(self.object)+1

        addItself=None

        if not o.isPrincipiaFolderish:
            if self.showFolderishChildrenOnly and self.showNonFolderishObject:
                addItself=o

            o=o.aq_parent

        siblings=self.getChildObjects(o,folderishOnly=self.showFolderishChildrenOnly)
        if addItself:
            siblings.append(addItself)

        res.append({'object':None,'siblings':siblings,'level':level,'siblingtitles':map(lambda x:x.title_or_id(),siblings)})
        itemcount=itemcount+len(siblings)

        return res,itemcount


    security.declarePublic('buildFlatMenuStructure')
    def buildFlatMenuStructure (self, batchSize=65535, batchStart=None ):
        """
        Constructs a Menu
        """
        #print 'build...'
        import time
        t=time.time()
        list,itemtotal = self.buildMenuStructure()

        l=[]
        res = {'list':l,'batchSize':batchSize,'batchStart':batchStart,'next':0,'prev':0}

        itemcounter=0
        menucounter=0
        curpos=0
        
        skipself = self.skipIndex_html and self.object.getId()=='index_html'

        # Opening
        for item in list :
            act = 0
            current=0

            for sibling in item['siblings'] :
                current = 0

                if self.skipIndex_html and sibling.getId()=='index_html':
                    continue

                if (sibling == item['object']) :
                    act = 1
                    if item==list[-2] and (skipself or self.showFolderishChildrenOnly and not self.showNonFolderishObject):
                        # deepest level
                        current=1
                        curpos=itemcounter

                else :
                    act = 0
                    current=0

                if sibling == self.object and not skipself and (self.showNonFolderishObject or not self.showFolderishChildrenOnly):
                    current=1
                    curpos=itemcounter

                if skipself and self.object == sibling:
                    continue
                
                lv = self.getLevel(sibling)
                r={'level':lv,'indent':lv - self.topLevel,'open':act,
                        'object':sibling,'title':sibling.title_or_id(),'iscurrent':current}

                if len(l) :
                    r['indentdiff'] = r['indent'] - l[-1]['indent']
                else:
                    r['indentdiff'] = 0
                    
                itemcounter = itemcounter + 1

                if r['level'] >= self.topLevel:
                    l.append(r)

                if (act == 1) :
                    break

        # Closing
        list.reverse()

        ready=0
        for item in list :
            act = 0
            if ready: break
            
            for sibling in item['siblings'] :

                if (sibling == item['object']) :
                    act = 1
                    continue

                if (act == 1) :
                    itemcounter = itemcounter + 1
                    lv = self.getLevel(sibling)

                    r={'level':lv,'indent':lv - self.topLevel,'open':0,'object':sibling}

                    if len(l) :
                        r['indentdiff'] = r['indent'] - l[-1]['indent']
                    else:
                        r['indentdiff']=0

                    if sibling:
                        r.update({'title':sibling.title_or_id()})

                    if r['level'] >= self.topLevel:
                        l.append(r)

        # and now extract the correct batch out of the data
        if batchStart is None:
            start=0
        else:
            start=batchStart
            
        end=start+batchSize
        
        if batchStart is None and not start <= curpos < end:
            res['prevBatchStart'] = max(start - batchSize, 0)
            res['prev']=1
            start = max(curpos - batchSize/2, 0)
            end=start + batchSize
        elif batchStart > 0:
            res['prev']=1
            res['prevBatchStart']=max(0,batchStart-batchSize)
        
        if end < len(l):
            res['nextBatchStart'] = end
            res['next']=1
            
        l = l[start:end]
        
        #force the parents to be in the list 
        if self.forceParentsInBatch and start and l[0]['indent']:
            for p in list[1:]:
                sibling=p['object']
                lv = self.getLevel(sibling)
                if lv < self.topLevel:
                    break
                
                if p != list[-1]:
                    indentdiff=1
                else:
                    indentdiff=0
                    
                r={'level':lv,'indent':lv - self.topLevel,'open':0,'object':sibling,'indentdiff':indentdiff}
                if not sibling in [o['object'] for o in l]:
                    l.insert(0,r)

        #set indentdiff for the first element
        if len(l):
            l[0]['indentdiff']=l[0]['indent']
            
        res['list']=l
        return res

allow_class(StatelessTreeBuilder)
