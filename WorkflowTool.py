from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from Products.CMFCore.WorkflowTool import WorkflowTool as BaseTool
from AccessControl import getSecurityManager
from Products.CMFCore.WorkflowCore import WorkflowException

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from PloneUtilities import log

try:
    from Products.CMFEventService.Events import ContentAddEvent as AddEvent
except:
    AddEvent=None

class WorkflowTool( BaseTool ):
    security = ClassSecurityInfo()
    plone_tool = 1

    security.declarePrivate('notifyCreated')
    def notifyCreated(self, ob):
        """ after the object has been created lets send an event if possible """
        BaseTool.notifyCreated(self, ob)

        portal_events=getToolByName(self, 'portal_events', None)
        if portal_events is not None and AddEvent:
            event=AddEvent(ob, context=ob.aq_parent)
            portal_events.publish(event)
            
    security.declarePublic('doActionFor')
    def doActionFor(self, ob, action, wf_id=None, *args, **kw):
        """ it appears that objects are reindexed after they
            are transitioned in DCWorkflow.  """
        result=BaseTool.doActionFor(self, ob, action, wf_id, *args, **kw)
        if result:
            result.reindexObjectSecurity()
            return result
        
    #XXX this should not make it into 1.0 
    # Refactor me, my maker was tired
    def flattenTransitions(self, objs, container=None): 
        """ this is really hokey - hold on!!"""
        if hasattr(objs, 'startswith'): 
            return ()

        transitions=[]
        t_names=[]

        if container is None:
            container = self
        for o in [getattr(container, oid, None) for oid in objs]:
            trans=()
            try:
                trans=self.getTransitionsFor(o, container)
            except: #yikes
                pass
            if trans:
                for t in trans:                   
                   if t['name'] not in t_names:
                      transitions.append(t)
                      t_names.append(t['name'])

        return tuple(transitions[:])

    security.declarePublic('getTransitionsFor')
    def getTransitionsFor(self, obj=None, container=None, REQUEST=None):
        if type(obj) is type([]):
            return self.flattenTransitions(objs=obj, container=container)
        result = {}
        chain = self.getChainFor(obj)
        for wf_id in chain:
            wf = self.getWorkflowById(wf_id)
            if wf is not None:
                sdef = wf._getWorkflowStateOf(obj)
                if sdef is not None:
                    for tid in sdef.transitions:
                        tdef = wf.transitions.get(tid, None)
                        if tdef is not None and \
                           tdef.trigger_type == TRIGGER_USER_ACTION and \
                           tdef.actbox_name and \
                           wf._checkTransitionGuard(tdef, obj) and \
                           not result.has_key(tdef.id):
                            result[tdef.id] = {
                                    'id': tdef.id,
                                    'title': tdef.title,
                                    'name': tdef.actbox_name
                                    }
        return tuple(result.values())
    
    def workflows_in_use(self):
        """ gathers all the available workflow chains (sequence of workflow ids, ).  """
        in_use = []
        types_tool = getToolByName(self, 'portal_types')

        in_use.append( self._default_chain )

        if self._chains_by_type:
            for chain in self._chains_by_type.values():
                in_use.append(chain)
        
        return tuple(in_use[:])

    security.declarePublic('getWorklists') 
    def getWorklists(self):
        """ instead of manually scraping actions_box, lets:
            query for all worklists in all workflow definitions.
            Returns a dictionary whos value is sequence of dictionaries

            i.e. map[workflow_id]=(workflow definition map, )
            each workflow defintion map contains the following:
            (worklist)id, guard (Guard instance), guard_permissions (permission of Guard instance), 
            catalog_vars (mapping), actbox_name (actions box label), and actbox_url (actions box url)
        """   
        wf_with_wlists = {}    
        for id in [workflow for seq in self.workflows_in_use() for workflow in seq]:
            # the above list incomprehension merely _flattens_ nested sequences into 1 sequence

            wf=self.getWorkflowById(id)
            if hasattr(wf, 'worklists'):
                wlists = []
                for worklist in wf.worklists._objects:
                    wlist_def=wf.worklists._mapping[worklist['id']]  
                    a_wlist = { 'id':worklist['id']
                              , 'guard' : wlist_def.getGuard()
                              , 'guard_permissions' : wlist_def.getGuard().getPermissionsText()
                              , 'catalog_vars' : wlist_def.var_matches
                              , 'name' : getattr(wlist_def, 'actbox_name', None)
                              , 'url' : getattr(wlist_def, 'actbox_url', None) }
                    wlists.append(a_wlist)
                # yes, we can duplicates, we filter duplicates out on the calling PyhtonScript client
                wf_with_wlists[id]=wlists 

        return wf_with_wlists

InitializeClass(WorkflowTool)

