#Stateless Tree Navigation
#(c) Philipp Auersperg phil@bluedynamics.com 10.09.2002

import string
from Globals import HTML
from AccessControl import ClassSecurityInfo,ModuleSecurityInfo,allow_class,allow_module

# to be able to import this stuff into python scripts
ModuleSecurityInfo('Products.CMFPlone').declarePublic('StatelessTreeNav')
ModuleSecurityInfo('Products.CMFPlone.StatelessTreeNav').declarePublic('StatelessTreeBuilder')
allow_module('Products.CMFPlone.StatelessTreeNav')

def wrap_obj(o,parent):
    return o.__of__(parent)

class StatelessTreeBuilder:
    """ builds a stateless tree structure for objects """
    
    security=ClassSecurityInfo()
    
    def __init__(self, object, topObject=None, topMetaType='CMF Site',
            maxcount=65535,includeTop=0,topLevel=0,listSiblings=1,
            childFinder=None,showFolderishSiblingsOnly=0,showFolderishChildrenOnly=0,
            showNonFolderishObject=0):
        self.object=object
        self.topObject=topObject
        self.topMetaType=topMetaType
        self.includeTop=includeTop
        self.maxcount=maxcount
        self.topLevel=topLevel
        self.listSiblings=listSiblings
        self.childFinder=childFinder
        self.showFolderishSiblingsOnly=showFolderishSiblingsOnly
        self.showFolderishChildrenOnly=showFolderishChildrenOnly
        self.showNonFolderishObject=showNonFolderishObject
        
    security.declarePublic('getLevel')
    def getLevel (self,object=None):
        """ 
        returns the depth of an object position relative to a given meta_type or object
        """
        
        count=0
        par = object or self.object
        
        while ( hasattr(par,'meta_type') and str(par.meta_type) != str(self.topMetaType) 
            and self.topObject != par and count < int(self.maxcount) ) :

          par=par.aq_parent
          count=count+1
        
        if int(self.includeTop):
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
            and self.topObject != par and count < int(self.maxcount) and level > self.topLevel) :
            res.append(par)
            par=par.aq_parent
            count=count+1
            level=level-1

        if int(self.includeTop):
            res.append(par)

        #pp.pprint(map(lambda x:x.title_or_id(),res))
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
    def buildFlatMenuStructure (self, batchSize=65535, batchStart=0 ):
        """
        Constructs a Menu
        """
        #print 'build...'
        import time
        t=time.time()
        
        list,itemtotal = self.buildMenuStructure()
        
        l=[]
        res = {'list':l,'batchSize':batchSize,'batchStart':batchStart,'next':0,'prev':0}
        
        if batchStart:
            res['prev']=1
            res['prevBatchStart']=max(0,batchStart-batchSize)
        
        itemcounter=0
        menucounter=0
        # Opening
        for item in list :
          act = 0
          current=0
        
          for sibling in item['siblings'] :

            current = 0

            if (sibling == item['object']) :
                act = 1

                if item==list[-2] and self.showFolderishChildrenOnly and not self.showNonFolderishObject:
                    # deepest level
                        current=1

            else :
                act = 0
                current=0

            if sibling == self.object and (self.showNonFolderishObject or not self.showFolderishChildrenOnly):
                current=1
            #print item['object'],map(lambda x:x['object'],list)
              
            r={'level':self.getLevel(sibling),'open':act,'object':sibling,'title':sibling.title_or_id(),'iscurrent':current}  
            itemcounter = itemcounter + 1

            if itemcounter > batchStart:
                l.append(r)
                
            if 0 and itemcounter >= batchStart+batchSize :
                res['nextBatchStart']=itemcounter
                res['next']=1
                return res
            
            if (act == 1) :
              break
        
        # Closing
        list.reverse()
        
        for item in list :
          act = 0  
        
          for sibling in item['siblings'] :

            if (sibling == item['object']) :
              act = 1
              continue
          
            if (act == 1) :
              itemcounter = itemcounter + 1
        
              r={'level':self.getLevel(sibling),'open':0,'object':sibling}

              if sibling:
                  r.update({'title':sibling.title_or_id()})
                  
              if itemcounter > batchStart:
                  l.append(r)

              if itemcounter >= batchStart+batchSize :
                  res['nextBatchStart']=itemcounter
                  res['next']=1
                  #print 'ready:',time.time()-t   
                  return res
                  
        #pp.pprint(res) 
        #print 'ready:',time.time()-t   
        return res

allow_class(StatelessTreeBuilder)
