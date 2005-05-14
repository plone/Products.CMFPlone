from Products.CMFCore.utils import _checkPermission, \
     _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from Products.CMFCore.WorkflowTool import WorkflowTool as BaseTool
from Products.CMFCore.WorkflowTool import WorkflowInformation
from Products.CMFPlone import ToolNames
from ZODB.POSException import ConflictError

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class WorkflowTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.WorkflowTool
    security = ClassSecurityInfo()
    plone_tool = 1
    toolicon = 'skins/plone_images/workflow_icon.gif'
    
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

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

        #XXX Need to behave differently for paths
        if len(objs) and '/' in objs[0]:
            return self.flattenTransitionsForPaths(objs)
        transitions=[]
        t_names=[]

        if container is None:
            container = self
        for o in [getattr(container, oid, None) for oid in objs]:
            trans=()
            try:
                trans=self.getTransitionsFor(o, container)
            except ConflictError:
                raise
            except:
                pass
            if trans:
                for t in trans:
                    if t['name'] not in t_names:
                        transitions.append(t)
                        t_names.append(t['name'])

        return tuple(transitions[:])


    def flattenTransitionsForPaths(self, paths):
        """ this is even more hokey!!"""
        if hasattr(paths, 'startswith'):
            return ()

        transitions=[]
        t_names=[]
        portal = getToolByName(self, 'portal_url').getPortalObject()

        for o in [portal.restrictedTraverse(path) for path in paths]:
            trans=()
            try:
                trans=self.getTransitionsFor(o, o.aq_inner.aq_parent)
            except ConflictError:
                raise
            except:
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
        info = WorkflowInformation(obj)
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
                                    'title_or_id': tdef.title_or_id(),
                                    'name': tdef.actbox_name,
                                    'url': tdef.actbox_url % info
                                    }
        return tuple(result.values())

    def workflows_in_use(self):
        """ gathers all the available workflow chains (sequence of workflow ids, ).  """
        in_use = []

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
            guard_roles (roles of Guard instance), catalog_vars (mapping), actbox_name (actions box label),
            actbox_url (actions box url) and types (list of portal types)
        """
        # We want to know which types use the workflows with worklists
        # This for example avoids displaying 'pending' of multiple workflows in the same worklist
        types_tool = getToolByName(self, 'portal_types')
        types_by_wf = {} # wf:[list,of,types]
        for t in types_tool.listContentTypes():
            for wf in self.getChainForPortalType(t):
                types_by_wf[wf] = types_by_wf.get(wf,[]) + [t]

        wf_with_wlists = {}
        for id in [workflow for seq in self.workflows_in_use() for workflow in seq]:
            # the above list incomprehension merely _flattens_ nested sequences into 1 sequence

            wf=self.getWorkflowById(id)
            if hasattr(wf, 'worklists'):
                wlists = []
                for worklist in wf.worklists._objects:
                    wlist_def=wf.worklists._mapping[worklist['id']]
                    # Make the var_matches a dict instead of PersistentMapping to enable access from scripts
                    var_matches = {}
                    for key in wlist_def.var_matches.keys(): var_matches[key] = wlist_def.var_matches[key]
                    a_wlist = { 'id':worklist['id']
                              , 'guard' : wlist_def.getGuard()
                              , 'guard_permissions' : wlist_def.getGuard().permissions
                              , 'guard_roles' : wlist_def.getGuard().roles
                              , 'catalog_vars' : var_matches
                              , 'name' : getattr(wlist_def, 'actbox_name', None)
                              , 'url' : getattr(wlist_def, 'actbox_url', None)
                              , 'types' : types_by_wf.get(id,[]) }
                    wlists.append(a_wlist)
                # yes, we can duplicates, we filter duplicates out on the calling PyhtonScript client
                wf_with_wlists[id]=wlists

        return wf_with_wlists

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getChainForPortalType')
    def getChainForPortalType(self, pt_name, managescreen=0):

        """ Get a chain for a specific portal type.
        """
        if self._chains_by_type.has_key(pt_name):
            return self._chains_by_type[pt_name]
        else:
            # (Default) is _not_ a chain nor a workflow in a chain.
            if managescreen:
                return '(Default)'
            else:
                # Return the default chain.
                return self._default_chain


    security.declareProtected(CMFCorePermissions.ManagePortal, 'listWorkflows')
    def listWorkflows(self):

        """ Return the list of workflows
        """
        return self.objectIds()

    security.declarePrivate('listActions')
    def listActions(self, info):

        """ Returns a list of actions to be displayed to the user.

        o Invoked by the portal_actions tool.
        
        o Allows workflows to include actions to be displayed in the
          actions box.

        o Object actions are supplied by workflows that apply to the object.
        
        o Global actions are supplied by all workflows.
        """
        show_globals = False
        chain = self.getChainFor(info.content)
        did = {}
        actions = []
        for wf_id in chain:
            did[wf_id] = 1
            wf = self.getWorkflowById(wf_id)
            if wf is not None:
                a = wf.listObjectActions(info)
                if a is not None:
                    actions.extend(a)
                if show_globals:
                    a = wf.listGlobalActions(info)
                    if a is not None:
                        actions.extend(a)

        if show_globals:
            wf_ids = self.getWorkflowIds()
            for wf_id in wf_ids:
                if not did.has_key(wf_id):
                    wf = self.getWorkflowById(wf_id)
                    if wf is not None:
                        a = wf.listGlobalActions(info)
                        if a is not None:
                            actions.extend(a)
        return actions

WorkflowTool.__doc__ = BaseTool.__doc__

InitializeClass(WorkflowTool)
